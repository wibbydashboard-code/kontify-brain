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
    Eres un Consultor Senior de Mentores Estratégicos.
    Usa el siguiente SOP para analizar los datos del lead de forma profesional, técnica y autoritaria.
    ---
    SOP DE REFERENCIA:
    {sop_content}
    ---
    DATOS DEL LEAD A ANALIZAR:
    {json.dumps(input_data, indent=2, ensure_ascii=False)}
    
    INSTRUCCIONES:
    1. Genera un 'Diagnostic Payload' en formato JSON estricto.
    2. Sigue el esquema definido en gemini.md.
    3. REGLA CRÍTICA: Si el lead dejó preguntas sin responder o respondió 'No' a controles básicos, señala explícitamente "RIESGO POR FALTA DE VISIBILIDAD" en el resumen.
    4. El pitch de venta debe ser agresivo y enfocado en la solución técnica prioritaria del SOP: {sop_path}.
    5. Nunca inventes datos financieros, básate solo en lo declarado.
    6. Formatea 'markdown_content' con una estructura premium para el administrador, usando tablas y encabezados claros.
    
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
