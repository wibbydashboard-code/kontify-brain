import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = '1zYPKfP1xObqhxkRNmaTjCbjI-jPR1Vec2c9uMHH0sVg'

def run_boot_test():
	creds = Credentials.from_service_account_file(
		'google_creds.json',
		scopes=['https://www.googleapis.com/auth/spreadsheets']
	)
	client = gspread.authorize(creds)
	client.open_by_key(SHEET_ID).sheet1.update_acell('A1', 'CONEXIÓN_TEST')

if __name__ == "__main__":
	run_boot_test()
