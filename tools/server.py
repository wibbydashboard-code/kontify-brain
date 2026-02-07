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
from sheets_connection_test import run_boot_test

# Asegurar que las carpetas existan
os.makedirs('.tmp', exist_ok=True)
REPORTS_DIR = os.path.join(os.getcwd(), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

try:
    run_boot_test()
    print("✅ BOOT-TEST: Google Sheets conectado y A1 actualizado.")
except Exception as e:
    print(f"🛑 CRITICAL ERROR: ERROR DE CREDENCIALES GOOGLE: {e}")

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "kontify-brain"}), 200

@app.route('/')
def serve_index():
    # En un entorno de desarrollo, el path relativo a public depende de donde se ejecute
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../public'))
    return send_from_directory(public_dir, 'index.html')

def _normalize_responses(raw_responses):
    normalized = []
    if isinstance(raw_responses, list):
        for item in raw_responses:
            if isinstance(item, dict):
                q = item.get('question') or item.get('q') or item.get('text')
                if not q:
                    q_index = item.get('q_index') or item.get('num') or item.get('id')
                    if q_index is not None:
                        q = f"Q{q_index}"
                a = item.get('answer') or item.get('a') or item.get('response') or item.get('value')

                if q or a is not None:
                    entry = {
                        "question": str(q).strip() if q else "N/A",
                        "answer": str(a).strip() if a is not None else "N/A"
                    }
                    if item.get('q_index') is not None:
                        entry["q_index"] = item.get('q_index')
                    if item.get('category_id') or item.get('cat'):
                        entry["category_id"] = item.get('category_id') or item.get('cat')
                    normalized.append(entry)
            elif isinstance(item, str):
                normalized.append({"question": item.strip(), "answer": "N/A"})
    return normalized

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
            error_msg = "Falta de Datos Maestros: RFC y Giro son obligatorios para el diagnóstico estratégico"
            log_entry = {
                "level": "error",
                "requestId": request_id,
                "error": "VALIDATION_ERROR",
                "message": error_msg,
                "missing": missing
            }
            print(json.dumps(log_entry, ensure_ascii=False))
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
        
        print(f"[{request_id}] 🧪 KONTIFY ENGINE v2.2.1 (MODO PRODUCCIÓN ACTIVO)")
        print(f"[{request_id}] 🔍 Validando Datos: Empresa={company_name_raw}, RFC={rfc}, Giro={giro}")

        # 2. PROCESAMIENTO IA (PMDS-IA)
        responses = _normalize_responses(data.get('responses', []))
        if not responses:
            error_msg = "BLOQUEO POR PROTOCOLO: Respuestas del cuestionario vacías o inválidas."
            print(f"[{request_id}] 🛑 ERROR DE VALIDACIÓN: {error_msg}")
            return jsonify({
                "status": "error",
                "message": error_msg,
                "requestId": request_id
            }), 400

        data_for_ai = dict(data)
        data_for_ai['responses'] = responses
        data_for_ai['lead_metadata'] = lead_meta

        print(json.dumps({"requestId": request_id, "payload_for_gemini": data_for_ai}, ensure_ascii=False))
        diagnostic_result = run_diagnostic(data_for_ai)
        if isinstance(diagnostic_result, dict) and diagnostic_result.get("error"):
            status_code = int(diagnostic_result.get("status_code", 500))
            print(f"[{request_id}] ⚠️ IA Falló: {diagnostic_result.get('error')}")
            if status_code == 422:
                return jsonify({
                    "status": "error",
                    "message": diagnostic_result.get("error"),
                    "requestId": request_id
                }), 422
            diagnostic_result = {
                "risk_assessment": {
                    "overall_risk_score": 55,
                    "risk_level": "VULNERABILIDAD DETECTADA",
                    "critical_finding": "Fallo IA: salida de contingencia activada.",
                    "hallazgos_tecnicos": [
                        "IA no respondió o respondió inválido.",
                        "Se generó un reporte mínimo para continuidad operativa.",
                        f"RFC Detectado: {rfc} - VALIDADO",
                        f"Giro Detectado: {giro} - REGISTRADO"
                    ]
                },
                "sales_pitch": "Se requiere reintento de diagnóstico con conectividad estable.",
                "markdown_content": "### CONTINGENCIA PMDS-IA\n- Se activó salida mínima por error en IA.\n- Verificar credenciales y salud de la API.",
                "admin_report": {
                    "summary": f"Fallo IA en solicitud {request_id}: {diagnostic_result.get('error')}"
                },
                "responses": responses,
                "lead_metadata": lead_meta
            }
        else:
            diagnostic_result['responses'] = responses
            diagnostic_result['lead_metadata'] = lead_meta
        
        # 2. Sincronizar CRM ANTES de generar PDF (Sync-First)
        try:
            host_url = request.host_url.rstrip('/')
            pdf_filename = f"KONTIFY_{company_name}_{request_id}.pdf"
            full_pdf_url = f"{host_url}/reports/{pdf_filename}"
            print(f"[{request_id}] 📊 Iniciando sincronización CRM...")
            sheets_ok = notify_all(diagnostic_result, full_pdf_url)
            if not sheets_ok:
                print(f"[{request_id}] 🛑 CRM Sync falló. Abortando PDF.")
                return jsonify({"status": "error", "message": "Error sincronizando CRM.", "requestId": request_id}), 502
            print(f"[{request_id}] ✅ Sincronización CRM completada.")
        except Exception as notify_err:
            print(f"[{request_id}] ⚠️ Error Registro: {str(notify_err)}")
            return jsonify({"status": "error", "message": "Error sincronizando CRM.", "requestId": request_id}), 502

        # 3. Generar PDF
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        
        try:
            generate_pdf_final(diagnostic_result, pdf_path)
        except Exception as pdf_err:
            print(f"[{request_id}] ❌ Error PDF: {str(pdf_err)}")
            return jsonify({"status": "error", "message": "Error al generar documento.", "requestId": request_id}), 500
        
        return jsonify({
            "status": "success",
            "version": "2.2.1",
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
    def _looks_like_options(opt_raw):
        opt_raw_upper = opt_raw.upper()
        return "OPTIONS" in opt_raw_upper or "|" in opt_raw

    def _parse_options_raw(opt_raw):
        opt_raw = re.sub(r'^\s*OPTIONS?\s*:\s*', '', opt_raw, flags=re.IGNORECASE).strip()
        if not opt_raw:
            return []
        return [o.strip() for o in opt_raw.split('|') if o.strip()]
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
                opt_same_line = re.search(r'\[([^\]]+)\]', full_text)
                if opt_same_line and _looks_like_options(opt_same_line.group(1)):
                    opt_raw = opt_same_line.group(1)
                    options = _parse_options_raw(opt_raw)
                    full_text = full_text.replace(opt_same_line.group(0), '').strip()
                else:
                    # REGLA 2: Opciones en la SIGUIENTE línea
                    # Verificamos si existe la siguiente línea y si tiene el tag [OPTIONS: ...] o simplemente [ ... ]
                    if i + 1 < len(lines):
                        next_line = lines[i+1].strip()
                        opt_next_line = re.search(r'\[([^\]]+)\]', next_line)
                        if opt_next_line and _looks_like_options(opt_next_line.group(1)):
                            opt_raw = opt_next_line.group(1)
                            options = _parse_options_raw(opt_raw)
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
