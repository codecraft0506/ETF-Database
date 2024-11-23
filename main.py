import requests
from bs4 import BeautifulSoup

# 定義目標 URL
url = "https://tw.stock.yahoo.com/quote/00937B.TWO/dividend"

# 發送 HTTP GET 請求
response = requests.get(url)

# 檢查請求是否成功
if response.status_code == 200:
    # 解析網頁內容
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
