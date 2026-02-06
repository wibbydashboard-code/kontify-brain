import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import sys
import io

# Forzar UTF-8 en salida estándar para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def notify_all(diagnostic_data, pdf_url):
    """Orquestador de notificaciones y registro de leads"""
    
    # Intentar extraer desde diferentes estructuras posibles
    payload = diagnostic_data.get('diagnostic_payload', {})
    
    # Lead Metadata
    lead = payload.get('lead_metadata', {})
    if not lead:
        # Fallback si la IA lo puso dentro de 'lead_assessment'
        lead = payload.get('lead_assessment', {})
    if not lead:
        lead = diagnostic_data.get('lead_metadata', {})

    # Report / Risk Data
    report = payload.get('risk_assessment', {})
    if not report:
        # Fallback si la IA usó 'lead_assessment' como contenedor de riesgo
        report = payload.get('lead_assessment', {})
    if not report:
        report = diagnostic_data.get('admin_report', {})

    # Campos específicos
    import datetime
    timestamp = lead.get('timestamp') or lead.get('fecha') or lead.get('date')
    if not timestamp:
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Búsqueda robusta de metadatos (IA puede variar nombres de llaves)
    company = lead.get('company_name') or lead.get('company') or report.get('company_name') or "N/A"
    rep_name = lead.get('contact_name') or lead.get('representative') or lead.get('name') or report.get('contact_name') or "N/A"
    email = lead.get('contact_email') or lead.get('email') or report.get('contact_email') or report.get('email') or "N/A"
    niche_id = lead.get('niche_id') or lead.get('industry') or "N/A"

    score = report.get('overall_risk_score', report.get('risk_score', 'N/A'))
    summary = report.get('summary', report.get('risk_level', report.get('recommendation', 'N/A')))
    
    pitch = payload.get('sales_pitch', '')
    if not pitch:
        pitch = report.get('pitch', '')
    if isinstance(pitch, dict):
        pitch = pitch.get('urgent_recommendation', '')
    
    recommended_service = "Específico por Nicho" # Fallback
    if score != 'N/A' and str(score).isdigit() and int(score) > 70:
        recommended_service = "Blindaje Gold / PropCo"
    
    # 1. Notificación Slack/WebHook
    send_webhook_notification(lead, score, recommended_service, pdf_url)
    
    # 2. Registro en Google Sheets
    lead_data = {
        "company": company,
        "niche": niche_id,
        "representative": rep_name,
        "email": email,
        "phone": lead.get('phone', 'N/A')
    }
    register_in_sheets(lead_data, score, summary, pdf_url, recommended_service, timestamp)
    
    # 3. Email de Cortesía (Simulado o vía Resend si hay API Key)
    send_courtesy_email(lead)

def send_webhook_notification(lead, score, recommended_service, pdf_url):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL no configurada.")
        return

    niche = lead.get('niche_id', 'Nicho Desconocido').upper()
    company = lead.get('company_name', 'Empresa Desconocida')
    
    message = f"🚀 *Nuevo Lead de [{niche}]:* {company}\n" \
              f"📊 *Riesgo:* {score}%\n" \
              f"💡 *Recomendación:* {recommended_service}\n" \
              f"📄 *PDF:* {pdf_url}"
              
    try:
        requests.post(webhook_url, json={"text": message})
        print("✅ Notificación de Webhook enviada.")
    except Exception as e:
        print(f"❌ Error enviando Webhook: {e}")

def register_in_sheets(lead, score, summary, pdf_url, recommended_service, timestamp):
    sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    creds_path = 'google_creds.json' # Debe ser proporcionado por el usuario
    
    if not sheets_id or not os.path.exists(creds_path):
        print("⚠️ Google Sheets no configurado (Falta ID o google_creds.json).")
        # Log local como fallback
        log_lead_locally(lead, score, summary, pdf_url)
        return

    try:
        from google.oauth2.service_account import Credentials
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheets_id).sheet1
        
        # Mapeo exacto según los encabezados del usuario:
        # A: Fecha y Hora
        # B: Empresa
        # C: Nicho
        # D: Representante
        # E: Email
        # F: Teléfono
        # G: Score de Riesgo
        # H: Hallazgo Crítico
        # I: Servicio Sugerido
        # J: Link al PDF
        
        row = [
            timestamp,                         # A: Fecha y Hora
            lead.get('company', ''),           # B
            lead.get('niche', ''),             # C
            lead.get('representative', ''),    # D
            lead.get('email', ''),             # E
            lead.get('phone', 'N/A'),          # F (Teléfono)
            score,                             # G (Score de Riesgo)
            summary[:150],                     # H (Hallazgo Crítico)
            recommended_service,                # I (Servicio Sugerido)
            pdf_url                            # J (Link al PDF)
        ]
        sheet.append_row(row)
        print("✅ Lead registrado en Google Sheets con mapeo corregido y robusto.")
    except Exception as e:
        import traceback
        print(f"❌ Error en Google Sheets: {e}")
        traceback.print_exc()

def log_lead_locally(lead, score, summary, pdf_url):
    log_path = 'leads_log.jsonl'
    log_entry = {
        "timestamp": lead.get('timestamp'),
        "company": lead.get('company_name'),
        "score": score,
        "pdf": pdf_url
    }
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')
    print(f"📝 Lead registrado localmente en {log_path}")

def send_courtesy_email(lead):
    # Simulación de envío de email
    email = lead.get('contact_email')
    name = lead.get('contact_name')
    print(f"📧 [Email de Cortesía] Enviado a {name} <{email}>: 'Gracias por su interés en Kontify. Un Mentor Estratégico lo contactará pronto.'")

if __name__ == "__main__":
    # Prueba rápida con datos simulados
    dummy_data = {
        "lead_metadata": {"company_name": "Empresa Test", "niche_id": "holding", "contact_email": "test@test.com"},
        "diagnostic_payload": {"risk_assessment": {"overall_risk_score": 85}}
    }
    notify_all(dummy_data, "http://localhost:5000/reports/test.pdf")
