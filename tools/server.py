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
    request_id = str(uuid.uuid4())[:8]
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Solicitud JSON vacía.", "requestId": request_id}), 400
            
        # 1. EXTRACCIÓN Y VALIDACIÓN DE DATOS MAESTROS (Middleware de Blindaje)
        # Prioridad a lead_metadata estructurado
        lead_meta = data.get('lead_metadata') or data.get('leadMetadata', {})
        
        # RFC Validation: Búsqueda robusta y sanitización
        rfc_raw = None
        for key in ['rfc', 'RFC']:
            rfc_raw = lead_meta.get(key)
            if rfc_raw: break
        if not rfc_raw: rfc_raw = data.get('rfc')
        
        # Sanitización de guiones y espacios
        rfc = str(rfc_raw).replace('-', '').replace(' ', '').upper() if rfc_raw else None
            
        # Giro (Actividad Principal)
        giro = lead_meta.get('main_activity') or lead_meta.get('activity')
        
        niche_id = lead_meta.get('niche_id')
        billing_range = lead_meta.get('billing_range')

        # PROTOCOLO DE BLINDAJE: Abortar si faltan datos críticos o son inválidos
        missing = []
        if not rfc or len(str(rfc).strip()) < 12: missing.append("RFC válido (min 12 caracteres)")
        if not giro: missing.append("Giro / Actividad Principal")
        if not niche_id: missing.append("Nicho")
        if not billing_range: missing.append("Rango de Facturación")
        
        if missing:
            error_msg = f"BLOQUEO POR PROTOCOLO: Faltan datos críticos: {', '.join(missing)}"
            print(f"[{request_id}] 🛑 ERROR DE VALIDACIÓN: {error_msg}")
            return jsonify({
                "status": "error", 
                "message": error_msg, 
                "requestId": request_id
            }), 400

        # Normalización de nombre para PDF y Trazabilidad
        company_name_raw = lead_meta.get('company_name', 'Lead_Report')
        company_name = "".join(c for c in str(company_name_raw) if c.isalnum() or c == ' ').strip().replace(' ', '_')
        
        # EL PASO MÁS IMPORTANTE: Normalizar campos para Notificator y PDF
        lead_meta['company'] = company_name_raw # notificator busca 'company'
        lead_meta['rfc'] = rfc                  # notificator busca 'rfc'
        lead_meta['activity'] = giro            # notificator busca 'activity'
        
        print(f"[{request_id}] 🧪 KONTIFY ENGINE v2.2.0 (MODO SIMULACIÓN ACTIVADO)")
        print(f"[{request_id}] 🔍 Validando Datos: Empresa={company_name_raw}, RFC={rfc}, Giro={giro}")

        # 2. PROCESAMIENTO IA (BLOQUEADO POR VALIDACIÓN DE COSTOS)
        # diagnostic_result = run_diagnostic(data)
        
        # MOCK FORZADO - NUNCA 0.0%
        diagnostic_result = {
            "risk_assessment": {
                "overall_risk_score": 88.5,
                "risk_level": "RIESGO CRÍTICO (SIMULACIÓN)",
                "critical_finding": "Validación de conexión Render-GitHub-Sheets activa.",
                "hallazgos_tecnicos": [
                    f"RFC Detectado: {rfc} - VALIDADO",
                    f"Giro Detectado: {giro} - REGISTRADO",
                    "Motor de IA: En espera de confirmación de CRM."
                ]
            },
            "sales_pitch": "PROCESO DE PRUEBA: El flujo de datos hacia Google Sheets está siendo auditado.",
            "markdown_content": "### AUDITORÍA DE INFRAESTRUCTURA\n- **Modo:** Zero-Cost Validation\n- **Target:** Columna K (RFC) y L (Giro)\n- **Estatus:** Transmitiendo...",
            "admin_report": {
                "summary": f"Sincronización manual: {company_name_raw}"
            },
            "responses": data.get('responses', []),
            "lead_metadata": lead_meta
        }
        
        # 2. Generar PDF
        pdf_filename = f"KONTIFY_{company_name}_{request_id}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        
        try:
            generate_pdf_final(diagnostic_result, pdf_path)
        except Exception as pdf_err:
            print(f"[{request_id}] ❌ Error PDF: {str(pdf_err)}")
            return jsonify({"status": "error", "message": "Error al generar documento.", "requestId": request_id}), 500
        
        # 3. Notificar y Registrar (Fallo Seguro)
        try:
            host_url = request.host_url.rstrip('/')
            full_pdf_url = f"{host_url}/reports/{pdf_filename}"
            print(f"[{request_id}] 📊 Iniciando sincronización CRM...")
            notify_all(diagnostic_result, full_pdf_url)
            print(f"[{request_id}] ✅ Sincronización CRM completada.")
        except Exception as notify_err:
            print(f"[{request_id}] ⚠️ Error Registro: {str(notify_err)}")
        
        return jsonify({
            "status": "success",
            "version": "2.2.0-SIM",
            "report_url": f"/reports/{pdf_filename}",
            "requestId": request_id
        })
    except Exception as e:
        print(f"[{request_id}] 🛑 Error Crítico: {str(e)}")
        return jsonify({"status": "error", "message": "Fallo interno de sistema.", "requestId": request_id}), 500

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
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detectar Categoría
            cat_match = re.search(r'##\s+\w*\.?\s*([^(]+)', line)
            if cat_match:
                current_category = cat_match.group(1).strip()
                i += 1
                continue
            
            # Detectar Pregunta: 1. ¿Pregunta?
            q_match = re.search(r'^(\d+)\.\s+(.+)$', line)
            if q_match:
                num = q_match.group(1)
                full_text = q_match.group(2).strip()
                options = []
                
                # REGLA 1: Opciones en la MISMA línea finalizando en [ ... ]
                # Ejemplo: 1. ¿Pregunta? [SÍ | NO] o 1. ¿Pregunta? [A | B]
                opt_same_line = re.search(r'\[([^\]]+)\]$', full_text)
                if opt_same_line:
                    opt_raw = opt_same_line.group(1)
                    if "OPTIONS:" in opt_raw:
                        opt_raw = opt_raw.replace("OPTIONS:", "").strip()
                    options = [o.strip() for o in opt_raw.split('|')]
                    full_text = full_text.replace(opt_same_line.group(0), '').strip()
                else:
                    # REGLA 2: Opciones en la SIGUIENTE línea
                    # Verificamos si existe la siguiente línea y si tiene el tag [OPTIONS: ...] o simplemente [ ... ]
                    if i + 1 < len(lines):
                        next_line = lines[i+1].strip()
                        opt_next_line = re.search(r'^\[(?:OPTIONS:\s*)?([^\]]+)\]$', next_line)
                        if opt_next_line:
                            opt_raw = opt_next_line.group(1)
                            options = [o.strip() for o in opt_raw.split('|')]
                            i += 1 # Consumimos la línea de opciones
                
                questions.append({
                    "q": full_text,
                    "num": num,
                    "cat": current_category,
                    "options": options
                })
            i += 1
                
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
