import os
import json
import sys
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    print("Error: Librería 'google-generativeai' no instalada.")
    sys.exit(1)

def run_diagnostic(input_data):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "tu_api_key_aqui":
        return {"error": "GEMINI_API_KEY no configurada"}

    genai.configure(api_key=api_key)
    
    niche_id = input_data.get('lead_metadata', {}).get('niche_id')
    sop_path = f'architecture/{niche_id}_sop.md'
    
    if not os.path.exists(sop_path):
        return {"error": f"SOP para nicho '{niche_id}' no encontrado en {sop_path}"}
        
    with open(sop_path, 'r', encoding='utf-8') as f:
        sop_content = f.read()

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    ESTÁS ACTUANDO COMO: Senior Executive Designer & Strategic Consultant (Nivel Big Four: Deloitte/EY).
    
    TU MISIÓN: Analizar los datos del lead a través del SOP para generar un reporte de ALTO IMPACTO que incite a la acción inmediata.
    
    SOP DE REFERENCIA:
    {sop_content}
    
    DATOS DEL LEAD A ANALIZAR:
    {json.dumps(input_data, indent=2, ensure_ascii=False)}
    
    REGLAS DE TONO Y ESTILO:
    1. TONO: Abandona el lenguaje pasivo. Usa verbos de acción y señala consecuencias financieras/legales claras.
    2. ESTRUCTURA: 
       - Cambia "Resumen Ejecutivo" por "DIAGNÓSTICO DE VULNERABILIDAD CRÍTICA".
       - En el SALES PITCH, destaca con lenguaje potente las frases que impliquen PÉRDIDA DE DINERO o RIESGO LEGAL GRAVE.
    3. REGLA CRÍTICA: Si el lead dejó preguntas sin responder o respondió 'No' a controles básicos, señala explícitamente "VULNERABILIDAD POR OPACIDAD DE CONTROL" o "RIESGO POR FALTA DE VISIBILIDAD".
    5. ANÁLISIS FINANCIERO: Utiliza los datos de Ventas, Utilidad, Activos, Pasivos y el Rango de Facturación (si se proporcionan) para identificar riesgos de insolvencia, apalancamiento excesivo o ineficiencia operativa. El Rango de Facturación debe servir para ponderar el impacto económico de los riesgos detectados.
    6. No inventes datos financieros, básate solo en los declarados.
    7. Formato JSON estricto para el 'Diagnostic Payload'.
    
    RESPONDE SOLO CON EL JSON.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Limpiar markdown si existe
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        diagnostic_result = json.loads(text)
        return diagnostic_result
    except Exception as e:
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
