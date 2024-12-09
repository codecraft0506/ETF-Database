import os
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

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
    return build('sheets', 'v4', credentials=creds)

# 讀取 Google Sheet 的數據
def read_sheet_data(service, spreadsheet_id, sheet_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1:Z"
    ).execute()
    data = result.get("values", [])
    return data

# 篩選和排序數據
def generate_monthly_performance_ranking(sheet_data, bond_type):
    # 欄位名稱映射
    column_mapping = {
        "前一年管理費": "內扣費用(%)",
        "一個月總報酬率": "月含息績效(%)",
        "年初至今總報酬率": "年含息績效(%)"
    }

    # 將數據轉換為 DataFrame
    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])

    # 根據是否為美國公債篩選數據
    df = df[df["是否為美國公債"] == bond_type]

    # 重命名欄位
    df.rename(columns=column_mapping, inplace=True)

    # 排序並新增排名
    df = df.sort_values(by="月含息績效(%)", ascending=False)
    df.insert(0, "月績效排名", range(1, len(df) + 1))
    df["內扣費用(%)"] = df["內扣費用(%)"].str.split('(').str[0].str.strip()
    # 選擇輸出的欄位順序
    output_columns = [
        "月績效排名", "基金代號", "基金名稱", "市價", "內扣費用(%)", "存續期間(年)",
        "近四季累積配息", "近四季殖利率", "月含息績效(%)", "年含息績效(%)"
    ]
    df = df[output_columns]
    # 將數據轉為列表格式
    final_data = [df.columns.tolist()] + df.values.tolist()
    return final_data

# 寫入數據到 Google Sheet
def write_to_sheet(service, spreadsheet_id, sheet_name, data):
    body = {"values": data}
    range_name = f"{sheet_name}!A1"
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()

# 主程式
if __name__ == "__main__":
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = "1RE6hoBhEANdKZ-dZsi-SilnX0HvQq8XpW1H7FoXn_vE"
    SOURCE_SHEET_NAME = "工作表1"

    TARGET_SHEET_US = "月績效排名-美國公債"
    TARGET_SHEET_NON_US = "月績效排名-非美國公債"

    # 加載環境變量
    load_dotenv("token1.env")

    # 初始化 Google Sheets API
    service = initialize_sheets_api(SCOPES)

    # 讀取表1數據
    sheet_data = read_sheet_data(service, SPREADSHEET_ID, SOURCE_SHEET_NAME)

    # 生成月績效排名 - 美國公債
    us_bonds_ranking = generate_monthly_performance_ranking(sheet_data, "美國公債")
    write_to_sheet(service, SPREADSHEET_ID, TARGET_SHEET_US, us_bonds_ranking)

    # 生成月績效排名 - 非美國公債
    non_us_bonds_ranking = generate_monthly_performance_ranking(sheet_data, "非美國公債")
    write_to_sheet(service, SPREADSHEET_ID, TARGET_SHEET_NON_US, non_us_bonds_ranking)
