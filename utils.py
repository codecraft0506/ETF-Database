def get_last_row(service, spreadsheet_id, sheet_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:A"  # 假設第一欄有資料
    ).execute()
    values = result.get('values', [])
    return len(values) + 1  # 加 1 以獲取下一行的位置


def append_to_sheet(service, data, spreadsheet_id, row_number, sheet_name):
    body = {
        'values': [data]
    }
    range_name = f"{sheet_name}!A{row_number}"
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()
