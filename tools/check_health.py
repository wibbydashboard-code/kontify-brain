import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

def check_health():
    load_dotenv()
    print("🚑 KONTIFY SYSTEM HEALTH CHECK")
    print("="*30)
    
    # 1. Verificar .env
    env_exists = os.path.exists(".env")
    print(f"[ ] Configuración .env: {'✅ CARGADA' if env_exists else '❌ NOT FOUND'}")
    
    # 2. Verificar Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            # Intento de generación mínima
            model.generate_content("ping")
            print("[ ] Gemini API: ✅ ACTIVA (gemini-2.0-flash)")
        except Exception as e:
            print(f"[ ] Gemini API: ❌ ERROR ({str(e)})")
    else:
        print("[ ] Gemini API: ❌ SIN KEY")

    # 3. Verificar Webhooks
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    print(f"[ ] Slack Webhook: {'✅ CONFIGURADO' if slack_url else '⚠️ NO CONFIGURADO (Solo Logs)'}")
    
    # 4. Verificar Google Sheets
    sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    creds_exist = os.path.exists("google_creds.json")
    print(f"[ ] Google Sheets: {'✅ LISTO' if (sheets_id and creds_exist) else '⚠️ INCOMPLETO (Faltan creds o ID)'}")

    # 5. Directorios Críticos
    dirs = ['architecture', 'tools', 'public/reports', '.tmp']
    for d in dirs:
        status = '✅' if os.path.exists(d) else '❌'
        print(f"[ ] Directorio {d}: {status}")

    print("="*30)
    print("Misión: 'Mentores Estratégicos' - System Pilot Out.")

if __name__ == "__main__":
    check_health()
