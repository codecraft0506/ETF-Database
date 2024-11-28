from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pandas as pd
# 設定憑證與範圍
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'starry-summer-437417-f1-abd378114258.json'

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# 1. 從來源 Google Sheet 抓取資料
def get_data_from_sheet(service, source_spreadsheet_id, source_range):
    result = service.spreadsheets().values().get(
        spreadsheetId=source_spreadsheet_id,
        range=source_range
    ).execute()
    data = result.get('values', [])
    if not data:
        print("來源工作表中沒有資料！")
        data = [["無資料"]]  # 預設值
    return data

# 2. 將資料寫入目標 Google Sheet
def write_to_target_sheet(service, target_spreadsheet_id, target_range, data):
    body = {
        'values': data
    }
    service.spreadsheets().values().update(
        spreadsheetId=target_spreadsheet_id,
        range=target_range,
        valueInputOption='RAW',
        body=body
    ).execute()
    print("資料已成功寫入目標 Google Sheet！")

# 主程式
source_spreadsheet_id = '1RE6hoBhEANdKZ-dZsi-SilnX0HvQq8XpW1H7FoXn_vE'  # 來源 Google Sheet ID
source_range = "'工作表1'"  # 確保使用引號包裹名稱

target_spreadsheet_id = '1DwDcSxlLrmuiVc7KVUmqitdH-2P8_eXHJyOxi2CYRa8'  # 目標 Google Sheet ID
target_range = "'工作表1'!A1"  # 確保使用引號包裹名稱，並從 A1 開始寫入

# 抓取來源資料
data = get_data_from_sheet(service, source_spreadsheet_id, source_range)

# 將 `data` 轉換為 pandas DataFrame
df = pd.DataFrame(data[1:], columns=data[0])  # 第 0 行作為欄位名稱，其餘作為數據

# 1. 篩選出「非美國公債」
filtered_df = df[df['是否為美國公債'] == '非美國公債']

# 2. 將「存續期間(年)」轉為數值類型（需要處理非數字情況）
filtered_df.loc[:, '存續期間(年)'] = pd.to_numeric(filtered_df['存續期間(年)'], errors='coerce')

# 3. 按「存續期間(年)」升序排序
sorted_df = filtered_df.sort_values(by='存續期間(年)')

# 4. 替換 NaN 值為空字串，避免 Google Sheets API 錯誤
sorted_df.fillna('', inplace=True)

# 顯示結果
#print(sorted_df)
result_data = [sorted_df.columns.tolist()] + sorted_df.values.tolist()
#print(result_data)
# 寫入目標 Google Sheet
write_to_target_sheet(service, target_spreadsheet_id, target_range, result_data)
