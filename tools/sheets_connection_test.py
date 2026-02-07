import os
import json
import base64
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = '1zYPKfP1xObqhxkRNmaTjCbjI-jPR1Vec2c9uMHH0sVg'

def _load_creds():
	creds_b64 = os.getenv("GOOGLE_CREDS_BASE64")
	creds_json = os.getenv("GOOGLE_CREDS_JSON")
	if creds_b64:
		info = json.loads(base64.b64decode(creds_b64).decode('utf-8'))
		return Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/spreadsheets'])
	if creds_json:
		info = json.loads(creds_json)
		return Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/spreadsheets'])
	raise ValueError("GOOGLE_CREDS_BASE64 o GOOGLE_CREDS_JSON no configurado")

def run_boot_test():
	creds = _load_creds()
	client = gspread.authorize(creds)
	client.open_by_key(SHEET_ID).sheet1.update_acell('A1', 'CONEXIÓN_TEST')

if __name__ == "__main__":
	run_boot_test()
