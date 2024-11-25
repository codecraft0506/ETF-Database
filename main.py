from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from get import scrape_page_data
# 設定 Google Sheets API 的範圍
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = "1RE6hoBhEANdKZ-dZsi-SilnX0HvQq8XpW1H7FoXn_vE"  # 替換為你的 Google Sheet ID
RANGE_NAME = '工作表1!A1'  # 要寫入的範圍

# 初始化 Google Sheets API
def initialize_sheets_api():
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

# 寫入數據到 Google Sheet
def write_to_sheet(service,data):
    body = {
        'values': [["債券分類", "基金名稱", "基金代號", "發行日期", "市價", "受益人數", "存續期間(年)", "平均票息率(%)"]]+data
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated.")

# 主程式
if __name__ == '__main__':
    service = initialize_sheets_api()
    data=scrape_page_data()
    #print(data)
    write_to_sheet(service,data)
