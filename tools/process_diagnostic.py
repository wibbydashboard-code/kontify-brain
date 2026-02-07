import os
import json
import sys
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    print("Error: Librería 'google-generativeai' no instalada.")
    sys.exit(1)

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

def run_diagnostic(input_data):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "tu_api_key_aqui":
        return {"error": "GEMINI_API_KEY no configurada"}

    genai.configure(api_key=api_key)
    
    lead_meta = input_data.get('lead_metadata', {})
    niche_id = lead_meta.get('niche_id', 'holding')
    main_activity = lead_meta.get('main_activity') or lead_meta.get('activity')
    rfc = lead_meta.get('rfc')

    if not rfc or not str(rfc).strip() or not main_activity or not str(main_activity).strip():
        return {"error": "Falta de Datos Maestros: RFC y/o Giro vacíos. Diagnóstico abortado antes de Gemini."}

    responses = _normalize_responses(input_data.get('responses', []))
    if not responses:
        return {"error": "Respuestas vacías o inválidas. El diagnóstico no puede continuar."}

    filled = [r for r in responses if str(r.get("answer", "")).strip() and str(r.get("answer", "")).strip().upper() != "N/A"]
    if len(filled) < 10:
        return {
            "error": "ERROR DE CAPTURA: El cuestionario llegó vacío al servidor",
            "status_code": 422
        }
    
    sop_path = f'architecture/{niche_id}_sop.md'
    if not os.path.exists(sop_path):
        sop_path = 'architecture/holding_sop.md' # Fallback
        
    with open(sop_path, 'r', encoding='utf-8') as f:
        sop_content = f.read()

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prompt evolucionado bajo PROTOCOLO MAESTRO IA SEGURO (PMDS-IA)
    company_name_str = lead_meta.get('company_name', 'Lead')
    prompt = f"""
    ROL: Senior Auditor & Strategic Risk Consultant (Big Four Style).
    OBJETIVO: Realizar un Diagnóstico de Robustez Corporativa para [{company_name_str}] en el nicho [{niche_id}].
    
    METODOLOGÍA (Ponderación Técnica):
     1. Evalúa los vectores de riesgo definidos en el SOP: {sop_content}
    2. Cruza con las respuestas reales (pueden ser SÍ/NO o MULTIOPCIÓN). Total respuestas: {len(responses)}. Datos: {json.dumps(responses, ensure_ascii=False)}
         - Si la respuesta es de opción múltiple (ej. "SAPI", "Régimen de Coordinados"), úsala tal cual.
         - No conviertas opciones múltiples a binario.
    3. Analiza el impacto financiero: {json.dumps(lead_meta.get('financial_data', {}), ensure_ascii=False)} | Rango: {lead_meta.get('billing_range', 'N/A')}.
    4. Considera la Actividad Principal: {main_activity}
    5. RFC (para trazabilidad y contexto fiscal): {rfc}
    
    REGLA DE CÁLCULO DE RIESGO:
    - 0-30%: Vigilancia Preventiva (Controles sólidos).
    - 31-70%: Vulnerabilidad Moderada (Deficiencias en procesos secundarios).
    - 71-100%: RIESGO CRÍTICO (Fallas en blindaje de activos, cumplimiento fiscal o gobernanza).
    
    INSTRUCCIONES ESTRÉCTAMENTE JSON:
    Retorna un JSON válido con esta estructura:
    {{
      "risk_assessment": {{
        "overall_risk_score": 0-100,
        "risk_level": "Nivel de riesgo",
        "critical_finding": "Hallazgo principal del diagnóstico",
        "hallazgos_tecnicos": [
           "Hallazgo 1 basado en SOP",
           "Hallazgo 2 basado en SOP"
        ]
      }},
      "sales_pitch": "Texto persuasivo de 2 frases sobre la urgencia de corrección.",
      "markdown_content": "### Análisis de Vulnerabilidad\\nContenido detallado en formato Markdown sin incluir el título principal.",
      "admin_report": {{
          "summary": "Resumen técnico para el CRM"
      }}
    }}
    
    IMPORTANTE: Si el cliente es 'Constructora Peña', analiza sus respuestas con RIGOR técnico. No uses mocks.
    """

    try:
        last_payload = {
            "lead_metadata": lead_meta,
            "responses": responses,
            "niche_id": niche_id,
            "main_activity": main_activity,
            "rfc": rfc,
            "prompt": prompt
        }
        with open('last_payload.json', 'w', encoding='utf-8') as f:
            json.dump(last_payload, f, indent=2, ensure_ascii=False)

        # Configuración de generación para forzar JSON
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=1000,
                temperature=0.2 # Más determinista
            )
        )
        
        text = response.text.strip()
        
        # Extracción robusta de JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        diagnostic_result = json.loads(text)
        
        # Validación de campos mínimos para evitar reportes vacíos
        if 'risk_assessment' not in diagnostic_result:
            diagnostic_result['risk_assessment'] = {"overall_risk_score": 50, "risk_level": "VULNERABILIDAD DETECTADA"}
        if 'overall_risk_score' not in diagnostic_result['risk_assessment']:
            diagnostic_result['risk_assessment']['overall_risk_score'] = 50
        else:
            try:
                if float(diagnostic_result['risk_assessment'].get('overall_risk_score', 0)) == 0:
                    diagnostic_result['risk_assessment']['overall_risk_score'] = 50
            except Exception:
                diagnostic_result['risk_assessment']['overall_risk_score'] = 50
            
        return diagnostic_result
    except Exception as e:
        print(f"❌ Error en IA: {str(e)}")
        return {"error": f"Error en procesamiento de IA: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python process_diagnostic.py [path_to_input_json]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: Archivo {input_file} no encontrado.")
        sys.exit(1)
        
    with open(input_file, 'r', encoding='utf-8') as f:
        input_json = json.load(f)
        
    result = run_diagnostic(input_json)
    
    # Guardar en .tmp
    output_filename = f"diagnostic_{input_json['lead_metadata']['company_name'].replace(' ', '_')}.json"
    output_path = os.path.join('.tmp', output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Diagnóstico procesado y guardado en: {output_path}")
