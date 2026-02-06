import os
import json
import gspread
from google.oauth2.service_account import Credentials

def test_sheets():
    sheets_id = "1zYPKfP1xObqhxkRNmaTjCbjI-jPR1Vec2c9uMHH0sVg"
    creds_path = 'google_creds.json'
    
    if not os.path.exists(creds_path):
        print(f"❌ Error: {creds_path} no encontrado.")
        return

    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        
        print(f"🔗 Conectando a la hoja: {sheets_id}...")
        sheet = client.open_by_key(sheets_id).sheet1
        
        test_row = ["TEST", "DEBUG", "CONEXIÓN", "OK", "EMAIL", "PHONE", "RFC", "ACTIVITY", "SERVICE", "PDF", "RFC_VAL", "ACT_VAL"]
        sheet.append_row(test_row)
        print("✅ Fila de prueba insertada exitosamente.")
        
    except Exception as e:
        print(f"❌ Error conectando a Google Sheets: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sheets()
