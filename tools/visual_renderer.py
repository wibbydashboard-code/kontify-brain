import os
import json
import jinja2 # Necesario para procesar templates, instalar si no está
import sys

def create_visual_prototype(json_path, template_path, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()

    # Procesamiento básico manual para evitar dependencia de jinja si no la instalé
    # En un entorno real usaríamos Jinja2 completo.
    
    # Extraer datos reales del JSON de Holding/Constructora
    payload = data.get('diagnostic_payload', data)
    
    risk_score = payload.get('risk_assessment', {}).get('overall_risk_score', payload.get('lead_score', 0))
    risk_level = payload.get('risk_assessment', {}).get('risk_level', "Riesgo Detectado")
    company_name = payload.get('lead_metadata', {}).get('company_name', "N/A")
    contact_name = payload.get('lead_metadata', {}).get('contact_name', "N/A")
    contact_email = payload.get('lead_metadata', {}).get('contact_email', "N/A")
    niche_id = payload.get('lead_metadata', {}).get('niche_id', "N/A")
    summary = payload.get('risk_assessment', {}).get('summary', payload.get('markdown_content', "")[:300] + "...")
    
    pitch = payload.get('sales_pitch', 'N/A')
    if isinstance(pitch, dict):
        pitch = pitch.get('urgent_recommendation', 'N/A')

    # Convertir hallazgos a filas de tabla
    findings_rows = ""
    findings = payload.get('risk_assessment', {}).get('key_risk_areas', [])
    if not findings: # Fallback para el formato de Holding
        if 'governance' in payload.get('risk_assessment', {}):
            gov = payload['risk_assessment']['governance']
            for k, v in gov.items():
                findings_rows += f"<tr><td>Gobernanza</td><td>{k}</td><td>{v[:100]}...</td></tr>"
            pat = payload['risk_assessment']['patrimonial']
            for k, v in pat.items():
                findings_rows += f"<tr><td>Patrimonial</td><td>{k}</td><td>{v[:100]}...</td></tr>"

    # Dash array para el semi-círculo de SVG (máximo es aprox 125 para el semicírculo)
    dash_val = (risk_score / 100) * 125
    dash_array = f"{dash_val}, 251"

    # Replacements
    html = template_str.replace("{{risk_score}}", str(risk_score))
    html = html.replace("{{risk_level}}", risk_level)
    html = html.replace("{{company_name}}", company_name)
    html = html.replace("{{contact_name}}", contact_name)
    html = html.replace("{{contact_email}}", contact_email)
    html = html.replace("{{niche_id}}", niche_id)
    html = html.replace("{{sales_pitch}}", pitch)
    html = html.replace("{{findings_rows}}", findings_rows)
    html = html.replace("{{summary}}", summary)
    html = html.replace("{{dash_array}}", dash_array)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Prototipo visual generado en: {output_path}")

if __name__ == "__main__":
    # Generar prototipo para Holding
    create_visual_prototype(
        '.tmp/diagnostic_Grupo_Familiar_Corporativo_S.A..json', 
        'architecture/admin_email_template.html', 
        '.tmp/prototype_holding_admin.html'
    )
