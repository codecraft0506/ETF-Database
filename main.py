import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from get import scrape_page_data
from utils import get_last_row, append_to_sheet
from googleapiclient.http import HttpRequest
import httplib2
from datetime import datetime
# 增加超時時間（例如，120秒）
httplib2.Http.timeout = 120
HttpRequest.http = httplib2.Http(timeout=120)
# 動態載入 .env 文件
def load_env_file(env_file):
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file)
    else:
        raise FileNotFoundError(f"{env_file} 不存在，請確認文件名稱和路徑正確")

# 初始化 Google Sheets API
def initialize_sheets_api(scopes):
    # 從環境變數讀取憑證資訊
    SERVICE_ACCOUNT_INFO = {
        "type": "service_account",
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('CLIENT_EMAIL')}",
    }
    # 建立憑證
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
    # 初始化 API
    service = build('sheets', 'v4', credentials=creds)
    return service

# 主程式
if __name__ == '__main__':
    # Google Sheets API 的範圍
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # 指定要使用的 .env 文件
    env_file = "token1.env"  # 或 "token2.env" 根據需求選擇
    load_env_file(env_file)

    # 初始化 Google Sheets API
    service = initialize_sheets_api(SCOPES)

    # 指定 Google Sheet 的 ID 和範圍
    SPREADSHEET_ID = "1RE6hoBhEANdKZ-dZsi-SilnX0HvQq8XpW1H7FoXn_vE"  # 替換為你的 Google Sheet ID
    SHEET_NAME = '工作表1'
    # 取得今日日期
    today_date = datetime.now().strftime("%Y%m%d")  # 格式為 YYYYMMDD
    # 如果第一行需要標題
    headers = ["抓取日期", "是否為美國公債", "債券分類", "基金名稱", "基金代號", "發行日期", "市價",f"受益人數({today_date})", "受益人數(上月底)", "受益人數(上上月底)", "平均票息率(%)","存續期間(年)", "當月配息金額", "當月殖利率", "填息天數(遠-近)", "資產規模", "除息日", "年化報酬率", "年初至今總報酬率", "一個月總報酬率","近四季累積配息","近四季殖利率","收益分配日", "前一年管理費", "保管銀行"]
    if get_last_row(service, SPREADSHEET_ID, SHEET_NAME) == 1:
        append_to_sheet(service, headers, SPREADSHEET_ID, 1, SHEET_NAME)
    # 調用 scrape_page_data
    scrape_page_data(service, SPREADSHEET_ID, SHEET_NAME)
    

