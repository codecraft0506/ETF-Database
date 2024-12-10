import os
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime
# 動態載入 .env 文件
# 取得今日日期
today_date = datetime.now().strftime("%Y%m%d")  # 格式為 YYYYMMDD
def load_env_file(env_file):
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file)
    else:
        raise FileNotFoundError(f"{env_file} 不存在，請確認文件名稱和路徑正確")

# 初始化 Google Sheets API
def initialize_sheets_api(scopes):
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
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
    service = build('sheets', 'v4', credentials=creds)
    return service

# 讀取 Google Sheet 的數據
def read_sheet_data(service, spreadsheet_id, sheet_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1:Z"
    ).execute()
    data = result.get("values", [])
    return data

# 處理數據
def process_bonds_data(sheet_data, bond_type):
    # 將數據轉換為 DataFrame
    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])  # 第一行為欄位名稱

    # 篩選數據
    bonds = df[df["是否為美國公債"] == bond_type].copy()

    # 確保「資產規模」為數字類型
    bonds["資產規模"] = bonds["資產規模"].str.replace(",", "").astype(float)

    # 按資產規模排序
    bonds.sort_values(by="資產規模", ascending=False, inplace=True)

    # 添加規模排名欄位
    bonds.insert(0, "規模排名", range(1, len(bonds) + 1))

    # 重命名欄位
    bonds = bonds.rename(columns={
        "基金代號": "代號",
        "基金名稱": "名稱",
        "資產規模": "淨值規模(億)上上月底",
    })

    # 新增「淨值規模(億)上個月底」欄位，所有值填入 0
    bonds["淨值規模(億)上月底"] = 0

    # 計算淨值規模(月增)
    bonds["淨值規模(月增)"] = bonds["淨值規模(億)上月底"] - bonds["淨值規模(億)上上月底"]
    # 確保受益人數欄位為數值型
    bonds[f"受益人數({today_date})"] = bonds[f"受益人數({today_date})"].str.replace(",", "").astype(float)
    
    # 確保「受益人數(上月底)」為數值型態
    bonds["受益人數(上月底)"] = bonds["受益人數(上月底)"].str.replace(",", "").astype(float)
    bonds["受益人數(上上月底)"] = bonds["受益人數(上上月底)"].str.replace(",", "").astype(float)
    bonds["受益人數(月增)"] = bonds["受益人數(上月底)"] - bonds["受益人數(上上月底)"]
    # 選取所需欄位
    columns_to_keep = [
        "規模排名", "代號", "名稱", "淨值規模(億)上上月底", "淨值規模(億)上月底",
        "淨值規模(月增)", "受益人數(上上月底)", "受益人數(上月底)", "受益人數(月增)"
    ]
    final_data = bonds[columns_to_keep]

    # 轉換為列表格式
    return [final_data.columns.tolist()] + final_data.values.tolist()

# 寫入數據到 Google Sheet
def write_to_sheet(service, spreadsheet_id, sheet_name, data):
    body = {"values": data}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"成功寫入 {result.get('updatedCells')} 個儲存格到 {sheet_name}。")

# 主程式
if __name__ == "__main__":
    # Google Sheets API 範圍
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # Google Sheet 的 ID 和工作表名稱
    SPREADSHEET_ID = "1RE6hoBhEANdKZ-dZsi-SilnX0HvQq8XpW1H7FoXn_vE"
    SOURCE_SHEET_NAME = "工作表1"

    TARGET_SHEET_US = "淨值規模排名-美國公債"
    TARGET_SHEET_NON_US = "淨值規模排名-非美國公債"

    # 載入 .env 文件
    load_env_file("token1.env")

    # 初始化 Google Sheets API
    service = initialize_sheets_api(SCOPES)

    # 讀取「工作表1」的數據
    sheet_data = read_sheet_data(service, SPREADSHEET_ID, SOURCE_SHEET_NAME)

    # 處理美國公債數據
    us_bonds_data = process_bonds_data(sheet_data, "美國公債")
    write_to_sheet(service, SPREADSHEET_ID, TARGET_SHEET_US, us_bonds_data)

    # 處理非美國公債數據
    non_us_bonds_data = process_bonds_data(sheet_data, "非美國公債")
    write_to_sheet(service, SPREADSHEET_ID, TARGET_SHEET_NON_US, non_us_bonds_data)