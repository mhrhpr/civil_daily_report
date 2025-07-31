import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# اتصال به Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# دو شیت: Contractor و DailyWorker
SHEET_URL = "https://docs.google.com/spreadsheets/d/1LM6Pbihi_gbFHHfLdYdVZiTRsNMRDM-TnCjEwJobLIg/"
contractor_sheet = client.open_by_url(SHEET_URL).worksheet("Contractor")
dailyworker_sheet = client.open_by_url(SHEET_URL).worksheet("DailyWorker")

def save_to_sheet(data: dict, report_type: str):
    sheet = contractor_sheet if report_type == "contractor" else dailyworker_sheet
    row = [data.get("telegram_id"), data.get("date")] + list(data.values())[2:]
    sheet.append_row(row)

