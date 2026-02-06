import os
import json
import requests
import gspread
from dotenv import load_dotenv
import sys
import io

# Forzar UTF-8 en salida estándar para Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def notify_all(diagnostic_data, pdf_url):
    """Orquestador de notificaciones y registro de leads"""
    
    # Prioridad absoluta a lead_metadata en la raíz (Datos reales del formulario)
    lead = diagnostic_data.get('lead_metadata', {})
    
    # Report / Risk Data (Datos generados por IA)
    payload = diagnostic_data.get('diagnostic_payload', {})
    if not payload: payload = diagnostic_data # Soporte si no hay anidación
    
    report = payload.get('risk_assessment', {})
    if not report: report = payload.get('lead_assessment', {})
    if not report: report = diagnostic_data.get('admin_report', {})

    # Campos específicos con fallbacks deterministas
    import datetime
    timestamp = lead.get('timestamp') or datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Búsqueda robusta de campos maestros (Match con server.py)
    company = str(lead.get('company_name') or lead.get('company') or "N/A")
    rep_name = str(lead.get('contact_name') or lead.get('representative') or "N/A")
    rep_role = str(lead.get('contact_role') or lead.get('role') or "N/A")
    email = str(lead.get('contact_email') or lead.get('email') or "N/A")
    phone = str(lead.get('contact_phone') or lead.get('phone') or "N/A")
    niche_id = str(lead.get('niche_id') or lead.get('niche') or "N/A")
    rfc = str(lead.get('rfc') or "N/A")
    activity = str(lead.get('main_activity') or lead.get('activity') or "N/A")

    # Datos financieros (Si existen)
    fin = lead.get('financial_data', {})
    billing = lead.get('billing_range') or fin.get('sales', 'N/A')

    score = report.get('overall_risk_score', report.get('risk_score', 'N/A'))
    summary = report.get('summary', report.get('risk_level', report.get('recommendation', 'N/A')))
    
    if isinstance(summary, dict):
        summary = json.dumps(summary, ensure_ascii=False)
    else:
        summary = str(summary)
    
    recommended_service = "Específico por Nicho"
    try:
        if score != 'N/A' and float(score) > 70:
            recommended_service = "Blindaje Gold / PropCo"
    except: pass
    
    # 1. Notificación Slack
    send_webhook_notification(lead, score, recommended_service, pdf_url)
    
    # 2. Registro en Google Sheets
    lead_data = {
        "company": company,
        "niche": niche_id,
        "representative": rep_name,
        "role": rep_role,
        "email": email,
        "phone": phone,
        "rfc": rfc,       # Columna K
        "activity": activity, # Columna L
        "billing": billing
    }
    
    print(f"📊 Orquestando registro en Sheets para: {company} | RFC: {rfc}")
    register_in_sheets(lead_data, score, summary, pdf_url, recommended_service, timestamp)
    
    # 3. Email de Cortesía
    send_courtesy_email(lead, pdf_url)

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
    sheets_id = os.getenv("GOOGLE_SHEETS_ID", "1zYPKfP1xObqhxkRNmaTjCbjI-jPR1Vec2c9uMHH0sVg")
    creds_path = 'google_creds.json'
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    
    if not (creds_json or os.path.exists(creds_path)):
        print("⚠️ Google Sheets no configurado (Faltan credenciales en ENV o archivo).")
        log_lead_locally(lead, score, summary, pdf_url)
        return

    try:
        from google.oauth2.service_account import Credentials
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        import json
        import re
        import base64

        creds_b64 = os.getenv("GOOGLE_CREDS_BASE64")
        
        if creds_b64:
            try:
                # 1. Intentar decodificar Base64 (Solución Robusta)
                decoded_json = base64.b64decode(creds_b64).decode('utf-8')
                info = json.loads(decoded_json)
                creds = Credentials.from_service_account_info(info, scopes=scope)
                print(f"🔐 CRM: Credenciales BASE64 cargadas ({info.get('client_email')})")
            except Exception as b64_err:
                print(f"⚠️ Fallo al decodificar GOOGLE_CREDS_BASE64: {b64_err}")
                creds = None
        
        if not globals().get('creds') and creds_json:
            try:
                # 2. Intentar JSON plano con reparación de saltos de línea
                creds_json_clean = re.sub(r'#.*', '', creds_json).strip()
                creds_json_clean = creds_json_clean.replace('\\\\n', '\\n').replace('\\n', '\n')
                info = json.loads(creds_json_clean)
                creds = Credentials.from_service_account_info(info, scopes=scope)
                print(f"🔐 CRM: Credenciales ENV (JSON) cargadas ({info.get('client_email')})")
            except Exception as json_err:
                print(f"⚠️ Fallo al parsear GOOGLE_CREDS_JSON: {json_err}")
                creds = None

        if not globals().get('creds') and os.path.exists(creds_path):
            # 3. Fallback a archivo local
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            print(f"📂 CRM: Credenciales ARCHIVO cargadas.")
        
        if not globals().get('creds'):
             raise ValueError("No se encontraron credenciales válidas (B64, ENV o Archivo)")
            
        client = gspread.authorize(creds)
        print(f"📊 CRM: Conectando a Sheet ID: {sheets_id}...")
        
        # Intento de apertura con manejo de errores específico
        try:
            spreadsheet = client.open_by_key(sheets_id)
            sheet = spreadsheet.get_worksheet(0) # Más seguro que .sheet1
            print(f"✅ CRM: Conectado exitosamente a '{spreadsheet.title}'")
        except Exception as sheet_err:
            print(f"🛑 CRM ERROR: No se pudo abrir la hoja. ¿ID correcto? ¿Compartida con el correo anterior? Error: {sheet_err}")
            raise sheet_err
        
        # Mapeo exacto según PROTOCOLO MAESTRO KONTIFY:
        # A: Fecha y Hora | B: Empresa | C: Nicho | D: Representante | E: Email | F: Teléfono
        # G: Score | H: Hallazgo | I: Servicio | J: Link PDF | K: RFC | L: Actividad Principal
        
        def safe_str(val):
            if val is None: return "N/A"
            s = str(val).strip()
            # Mantener caracteres latinos (acentos, ñ) pero filtrar basura
            return "".join(c for c in s if c.isprintable() or c.isspace())

        row = [
            safe_str(timestamp),                         # A (0)
            safe_str(lead.get('company', 'N/A')),        # B (1)
            safe_str(lead.get('niche', 'N/A')),          # C (2)
            safe_str(f"{lead.get('representative', 'N/A')} ({lead.get('role', 'N/A')})"), # D (3)
            safe_str(lead.get('email', 'N/A')),          # E (4)
            safe_str(lead.get('phone', 'N/A')),          # F (5)
            safe_str(score),                             # G (6)
            safe_str(summary[:400]),                     # H (7) - Ampliado para más detalle
            safe_str(recommended_service),               # I (8)
            safe_str(pdf_url),                           # J (9)
            safe_str(lead.get('rfc', 'N/A')),            # K (10)
            safe_str(lead.get('activity', 'N/A'))        # L (11)
        ]
        
        try:
            sheet.append_row(row, value_input_option='RAW')
            print(f"✅ Lead [{lead.get('company')}] registrado en Google Sheets (Fila Lote).")
        except Exception as api_err:
            if "403" in str(api_err):
                print(f"🛑 ERROR DE ACCESO (403): La cuenta de servicio {creds.service_account_email} no tiene permisos de EDITOR en el documento.")
            raise api_err

    except Exception as e:
        print(f"❌ Error Crítico en Google Sheets: {str(e)}")
        log_lead_locally(lead, score, summary, pdf_url) # Fallback seguro

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

def send_courtesy_email(lead, pdf_url):
    """Envío real de email vía SendGrid"""
    api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "contacto@mentoresestrategicos.com") # Default
    
    if not api_key:
        print("⚠️ SENDGRID_API_KEY no configurada. Saltando envío de email.")
        return

    email = lead.get('contact_email') or lead.get('email')
    name = lead.get('contact_name') or lead.get('representative')
    
    if not email:
        print("⚠️ No se encontró email del lead para enviar cortesía.")
        return

    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=sender_email,
        to_emails=email,
        subject='Tu Diagnóstico de Riesgo Kontify está listo 💼',
        html_content=f"""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #c1ff72; background: #000; padding: 10px;">¡Hola {name}!</h2>
                <p>Gracias por completar el diagnóstico de riesgo con <strong>Kontify - Mentores Estratégicos</strong>.</p>
                <p>Tu reporte detallado ya ha sido procesado por nuestra Inteligencia Artificial y está disponible para descarga:</p>
                <a href="{pdf_url}" style="display: inline-block; padding: 12px 20px; background-color: #000; color: #fff; text-decoration: none; border-radius: 5px; font-weight: bold;">📥 Descargar mi Reporte PDF</a>
                <p>En breve, uno de nuestros consultores senior se pondrá en contacto contigo para profundizar en los hallazgos críticos.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #888;">Este es un correo automático de Kontify. Si no solicitaste este diagnóstico, por favor ignora este mensaje.</p>
            </div>
        """
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"✅ Email enviado a {email} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error enviando email con SendGrid: {e}")

if __name__ == "__main__":
    # Prueba rápida con datos simulados
    dummy_data = {
        "lead_metadata": {"company_name": "Empresa Test", "niche_id": "holding", "contact_email": "test@test.com"},
        "diagnostic_payload": {"risk_assessment": {"overall_risk_score": 85}}
    }
    notify_all(dummy_data, "http://localhost:5000/reports/test.pdf")
