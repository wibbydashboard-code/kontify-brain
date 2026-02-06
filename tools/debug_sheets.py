import os
import gspread
import traceback
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

def debug_gspread():
    load_dotenv()
    sheets_id = os.getenv('GOOGLE_SHEETS_ID')
    creds_path = 'google_creds.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    print(f"DEBUG: Sheets ID: '{sheets_id}'")
    print(f"DEBUG: Creds Path: '{creds_path}'")
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        print("DEBUG: Auth successful")
        
        ss = client.open_by_key(sheets_id)
        print(f"DEBUG: Spreadsheet Title: {ss.title}")
        
    except Exception as e:
        print(f"DEBUG: Caught exception of type: {type(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_gspread()
