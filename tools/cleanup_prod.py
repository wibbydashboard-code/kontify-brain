import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

def cleanup_production():
    load_dotenv()
    print("🧹 INICIANDO LIMPIEZA DE AUDITORÍA (PROD READY)...")
    
    # 1. Limpiar Google Sheet
    sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    creds_path = 'google_creds.json'
    
    if sheets_id and os.path.exists(creds_path):
        try:
            scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            client = gspread.authorize(creds)
            ss = client.open_by_key(sheets_id)
            sheet = ss.sheet1
            
            # Mantener encabezados (Fila 1), borrar todo lo demás
            rows = len(sheet.get_all_values())
            if rows > 1:
                sheet.delete_rows(2, rows)
                print(f"✅ Google Sheet limpiado ({rows-1} filas eliminadas).")
            else:
                print("✅ Google Sheet ya está vacío (solo encabezados).")
        except Exception as e:
            print(f"❌ Error limpiando Google Sheet: {e}")
    
    # 2. Limpiar Log Local
    log_path = 'leads_log.jsonl'
    if os.path.exists(log_path):
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("")
        print("✅ Log local (leads_log.jsonl) reiniciado.")
    
    # 3. Limpiar archivos temporales
    tmp_dir = '.tmp'
    if os.path.exists(tmp_dir):
        files = os.listdir(tmp_dir)
        for f in files:
            file_path = os.path.join(tmp_dir, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {f}: {e}")
        print("✅ Archivos temporales (.tmp) eliminados.")

    print("🏁 LIMPIEZA COMPLETADA. KONTIFY ESTÁ EN CERO.")

if __name__ == "__main__":
    cleanup_production()
