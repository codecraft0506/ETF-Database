import os
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# 初始化 Google Sheets API
# 動態載入 .env 文件
def load_env_file(env_file):
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file)
    else:
        raise FileNotFoundError(f"{env_file} 不存在，請確認文件名稱和路徑正確")
# 讀取整個工作表內容
def read_sheet_data(service, spreadsheet_id, sheet_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1:Z"  # 假設資料在 A 到 Z 欄之間
    ).execute()
    data = result.get("values", [])
    return data
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
def filter_and_transform_data(sheet_data, selected_columns, column_mapping, filter_condition):
    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
    # 篩選指定欄位並過濾條件
    filtered_df = df[df["債券分類"].str.contains(filter_condition, na=False)][selected_columns]
    filtered_df.rename(columns=column_mapping, inplace=True)
    transposed_df = filtered_df.T
    transposed_df.reset_index(inplace=True)
    transposed_df.columns = ["欄位名稱"] + [f"值{i+1}" for i in range(len(transposed_df.columns) - 1)]
    return transposed_df.values.tolist()
# 寫入直向資料到 Google Sheet
def write_vertical_data(service, spreadsheet_id, sheet_name, data):
    body = {
        "values": data
    }
    range_name = f"{sheet_name}!A1"  # 從 A1 開始寫入
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"成功寫入 {result.get('updatedCells')} 個儲存格。")

# 主程式
if __name__ == "__main__":
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = "1RE6hoBhEANdKZ-dZsi-SilnX0HvQq8XpW1H7FoXn_vE"
    SOURCE_SHEET_NAME = "工作表1"
    env_file = "token1.env"
    load_env_file(env_file)
    service = initialize_sheets_api(SCOPES)

    # 讀取數據
    sheet_data = read_sheet_data(service, SPREADSHEET_ID, SOURCE_SHEET_NAME)

    # 定義選擇欄位和映射
    selected_columns = [
        "基金名稱", "發行日期", "市價", "資產規模", "受益人數(上月底)",
        "前一年管理費", "平均票息率(%)", "當月殖利率", "近四季殖利率",
        "填息天數(遠-近)", "存續期間(年)", "保管銀行", "除息日", "收益分配日"
    ]
    column_mapping = {
        "資產規模": "資產規模(億)",
        "當月殖利率": "11月殖利率(%)",
        "近四季殖利率": "近四季累積殖利率(%)",
    }

    # 美國公債
    us_bonds_data = filter_and_transform_data(sheet_data, selected_columns, column_mapping, "公債")
    write_vertical_data(service, SPREADSHEET_ID, "當月配息-美國公債", us_bonds_data)

    # 公司債
    corporate_bonds_data = filter_and_transform_data(sheet_data, selected_columns, column_mapping, "公司債")
    write_vertical_data(service, SPREADSHEET_ID, "當月配息-公司債", corporate_bonds_data)

    # 新興公司債
    emerging_bonds_data = filter_and_transform_data(sheet_data, selected_columns, column_mapping, "新興市場債")
    write_vertical_data(service, SPREADSHEET_ID, "當月配息-新興公司債", emerging_bonds_data)
