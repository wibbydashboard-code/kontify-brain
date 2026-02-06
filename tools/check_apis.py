import gspread
import traceback
from google.oauth2.service_account import Credentials

def check_apis():
    creds_path = 'google_creds.json'
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        print("Authenticating...")
        
        print("Testing Google Sheets & Drive API...")
        ss = client.create('KONTIFY_API_CHECK')
        print(f"API ENABLED! Created sheet: {ss.id}")
        client.del_spreadsheet(ss.id)
    except Exception as e:
        print(f"API ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    check_apis()
