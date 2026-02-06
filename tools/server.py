from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import uuid
import sys

# Configuración de la Aplicación
app = Flask(__name__)
# Configuración de orígenes permitidos (CORS) para producción
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Agregar el directorio /tools al path para importaciones internas
tools_dir = os.path.dirname(os.path.abspath(__file__))
if tools_dir not in sys.path:
    sys.path.append(tools_dir)

from process_diagnostic import run_diagnostic
from pdf_generator_v2 import generate_pdf_final
from notificator import notify_all

# Asegurar que las carpetas existan
os.makedirs('.tmp', exist_ok=True)
REPORTS_DIR = os.path.join(os.getcwd(), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "kontify-brain"}), 200

@app.route('/')
def serve_index():
    # En un entorno de desarrollo, el path relativo a public depende de donde se ejecute
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../public'))
    return send_from_directory(public_dir, 'index.html')

@app.route('/api/submit', methods=['POST'])
def submit_quiz():
    try:
        data = request.json
        company_name = data.get('lead_metadata', {}).get('company_name', 'Lead').replace(' ', '_')
        
        # 1. Procesar Diagnóstico con IA
        diagnostic_result = run_diagnostic(data)
        
        # ASEGURAR METADATOS: Fusionar metadata original si la IA la omitió
        if 'lead_metadata' not in diagnostic_result:
            diagnostic_result['lead_metadata'] = data.get('lead_metadata', {})
        else:
            # Si existe, nos aseguramos de que tenga los datos financieros originales
            diagnostic_result['lead_metadata'].update(data.get('lead_metadata', {}))
        
        # 2. Generar PDF
        pdf_filename = f"KONTIFY_Report_{company_name}_{uuid.uuid4().hex[:6]}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        
        generate_pdf_final(diagnostic_result, pdf_path)
        
        # 3. Notificar y Registrar (Nueva Integración)
        host_url = request.host_url.rstrip('/')
        full_pdf_url = f"{host_url}/reports/{pdf_filename}"
        notify_all(diagnostic_result, full_pdf_url)
        
        # 4. Limpieza de .tmp (Opcional, manteniendo integridad)
        # En una versión de producción moveríamos aquí los archivos temporales
        
        return jsonify({
            "status": "success",
            "message": "Diagnóstico procesado exitosamente",
            "report_url": f"/reports/{pdf_filename}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/questions/<niche_id>', methods=['GET'])
def get_questions(niche_id):
    mapping = {
        "holding": "holding_grupo_diagnostico.md",
        "constructora": "constructora_diagnostico.md",
        "autotransporte": "autotransporte_diagnostico.md",
        "comercializadora": "comercializadora_diagnostico.md",
        "manufactura": "manufactura_transformacion_diagnostico.md"
    }
    
    filename = mapping.get(niche_id)
    if not filename:
        return jsonify({"error": "Nicho no encontrado"}), 404
    
    base_dir = os.getcwd()
    file_path = os.path.join(base_dir, filename)
    
    # Intento 2: Buscar en el directorio superior si estamos en /tools/
    if not os.path.exists(file_path):
        file_path = os.path.join(os.path.dirname(base_dir), filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Archivo de diagnóstico no encontrado"}), 404
        
    import re
    questions = []
    current_category = "General"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Detectar Categoría
            cat_match = re.search(r'##\s+\w+\.\s+([^(]+)', line)
            if cat_match:
                current_category = cat_match.group(1).strip()
                continue
            
            # Detectar Pregunta
            q_match = re.search(r'^(\d+)\.\s+(.+)$', line)
            if q_match:
                questions.append({
                    "q": q_match.group(2).strip(),
                    "cat": current_category
                })
                
        return jsonify(questions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reports/<path:path>')
def serve_reports(path):
    return send_from_directory(REPORTS_DIR, path)

@app.route('/<path:path>')
def serve_static(path):
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../public'))
    return send_from_directory(public_dir, path)

import logging

# Configuración de Logs para Producción
if os.getenv("FLASK_ENV") == "production":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.logger.setLevel(logging.ERROR)

if __name__ == '__main__':
    is_prod = os.getenv("FLASK_ENV") == "production"
    port = int(os.getenv("PORT", 5000))
    
    if is_prod:
        print("🚀 KONTIFY SERVER: MODE PRODUCTION ACTIVE")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        app.run(port=port, debug=True)
