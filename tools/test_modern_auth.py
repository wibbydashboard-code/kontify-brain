import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

def test_new_auth():
    load_dotenv()
    sheets_id = os.getenv('GOOGLE_SHEETS_ID')
    creds_path = 'google_creds.json'
    
    # Nuevo método de autenticación recomendado por Google
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        
        print(f"Connecting to: {sheets_id}")
        ss = client.open_by_key(sheets_id)
        print(f"SUCCESS! Spreadsheet: {ss.title}")
        
    except Exception as e:
        print(f"FAILED: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_auth()
