import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
# 取得今天的日期
today_date = datetime.now().date()
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

# 篩選和轉換數據
def filter_and_transform_data(sheet_data, selected_columns, column_mapping, filter_condition, current_month):
    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
    df["前一年管理費"] = df["前一年管理費"].str.split('(').str[0].str.strip()
    # 轉換「除息日」為日期格式
    df["除息日"] = pd.to_datetime(df["除息日"], errors="coerce", format="%Y/%m/%d")
    # 確保「抓取日期」是日期格式（假設格式為 yyyymmdd）
    df["抓取日期"] = pd.to_datetime(df["抓取日期"], format="%Y%m%d", errors="coerce")
    #yesterday_date = (datetime.now() - timedelta(days=1)).date()
    # 篩選指定條件
    filtered_df = df[
        (df["債券分類"].str.contains(filter_condition, na=False)) & 
        (df["除息日"].dt.month == current_month) &
        (df["抓取日期"].dt.date == today_date)
    ][selected_columns]
    #print(filtered_df)
    filtered_df["除息日"] = filtered_df["除息日"].dt.strftime("%Y/%m/%d")
    
    # 重命名欄位
    filtered_df.rename(columns=column_mapping, inplace=True)
    
    # 轉置數據
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

    # 獲取當前月份
    current_month = datetime.now().month
    today = datetime.now().date().strftime("%Y%m%d")
    # 定義選擇欄位和映射
    selected_columns = [
        "基金名稱", "基金代號", "發行日期", "市價", "資產規模", f"受益人數({today})",
        "前一年管理費", "平均票息率(%)", "當月殖利率", "近四季殖利率",
        "填息天數(遠-近)", "存續期間(年)", "保管銀行", "除息日", "收益分配日"
    ]
    column_mapping = {
        "資產規模": "資產規模(億)",
        "近四季殖利率": "近四季累積殖利率(%)",
        "市價":f"{today_date}市價",
    }

    # 美國公債
    us_bonds_data = filter_and_transform_data(sheet_data, selected_columns, column_mapping, "公債", current_month)
    write_vertical_data(service, SPREADSHEET_ID, "當月配息-美國公債", us_bonds_data)

    # 公司債
    corporate_bonds_data = filter_and_transform_data(sheet_data, selected_columns, column_mapping, "公司債", current_month)
    write_vertical_data(service, SPREADSHEET_ID, "當月配息-公司債", corporate_bonds_data)

    # 新興市場債
    emerging_bonds_data = filter_and_transform_data(sheet_data, selected_columns, column_mapping, "新興市場債", current_month)
    write_vertical_data(service, SPREADSHEET_ID, "當月配息-新興公司債", emerging_bonds_data)
