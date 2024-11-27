from scrapling import Adaptor
from playwright.sync_api import sync_playwright
import time

url = "https://www.macromicro.me/etf/tw/intro/00679B"

# 使用 Playwright 進行瀏覽器自動化
with sync_playwright() as p:
    try:
        # 初始化瀏覽器（非無頭模式）
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 瀏覽目標網頁
        page.goto(url)
        
        # 模擬人類行為的等待時間
        time.sleep(3)
        
        # 使用 CSS 選擇器點擊導航按鈕
        page.click('#nav-dividend')
        
        # 等待股利內容加載
        page.wait_for_selector('#content--dividend div.your-target-class', timeout=10000)
        time.sleep(3)  # 額外等待，以確保內容完全加載
        
        # 獲取更新後的 HTML 內容
        content = page.content()
        
        # 初始化 Adaptor 解析 HTML
        adaptor = Adaptor(content, url=url)
        
        # 使用 CSS 選擇器找到股利內容
        data_element = adaptor.css('#content--dividend div.your-target-class', auto_match=True)
        
        if data_element:
            data = data_element.text.strip()
            print(data)
        else:
            print("未找到股利內容")
        
    except Exception as e:
        print(f"發生錯誤: {e}")
    
    finally:
        browser.close()
