import os
import json
import sys
from dotenv import load_dotenv

# Nota: El System Pilot usa la API de Gemini para procesamiento determinista
try:
    import google.generativeai as genai
except ImportError:
    print("Error: Librería 'google-generativeai' no instalada.")
    sys.exit(1)

def handshake():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ Error: GEMINI_API_KEY no encontrada en .env")
        return False

    genai.configure(api_key=api_key)
    
    # Cargar SOP y Lead de prueba
    try:
        with open('architecture/constructora_sop.md', 'r', encoding='utf-8') as f:
            sop_content = f.read()
            
        with open('.tmp/test_lead_constructora.json', 'r', encoding='utf-8') as f:
            lead_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Error: Archivo no encontrado: {e.filename}")
        return False

    print("🔗 Iniciando Handshake con Gemini API...")
    
    # Configuración de la IA
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Eres un {lead_data['lead_metadata']['niche_id']} Senior.
    Usa el siguiente SOP para analizar los datos del lead:
    ---
    {sop_content}
    ---
    DATOS DEL LEAD:
    {json.dumps(lead_data, indent=2)}
    
    INSTRUCCIÓN: Genera un Diagnostic Payload en formato JSON estricto siguiendo el esquema de gemini.md.
    Asegúrate de que el sales_strategy.pitch sea agresivo y enfocado en Blindaje Patrimonial/PropCo dado el perfil de riesgo.
    """

    try:
        response = model.generate_content(prompt)
        diagnostic_text = response.text
        
        # Intentar limpiar si la IA devuelve markdown
        if "```json" in diagnostic_text:
            diagnostic_text = diagnostic_text.split("```json")[1].split("```")[0].strip()
        
        # Validar JSON
        diagnostic_json = json.loads(diagnostic_text)
        
        # Guardar resultado
        output_path = '.tmp/test_diagnostic_result.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(diagnostic_json, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Handshake Exitoso. Diagnóstico generado en: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la generación: {str(e)}")
        return False

if __name__ == "__main__":
    if handshake():
        sys.exit(0)
    else:
        sys.exit(1)
