from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests
from get_data import get_data
from get_time import get_time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# 定義函數抓取單頁數據
def scrape_page_data():
    # 指定 ChromeDriver 的路徑
    driver_path = r".\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    service = Service(driver_path)
    # 設定選項
    options = Options()
    options.add_argument('--headless')  # 啟用無頭模式
    options.add_argument('--disable-gpu')  # 如果你使用的是 Windows，需要禁用 GPU
    options.add_argument('--disable-dev-shm-usage')  # 防止共享內存問題
    # 初始化 WebDriver
    driver = webdriver.Chrome(service=service,options=options)
    ETF=["公債","投資型公司債","新興市場債",]
    request_href=[
        "https://www.cmoney.tw/etf/tw/filter/bond?key=%E5%85%AC%E5%82%B5",
        "https://www.cmoney.tw/etf/tw/filter/bond?key=%E6%8A%95%E8%B3%87%E7%B4%9A%E5%85%AC%E5%8F%B8%E5%82%B5",
        "https://www.cmoney.tw/etf/tw/filter/bond?key=%E6%96%B0%E8%88%88%E5%B8%82%E5%A0%B4%E5%82%B5"      
        ]
    check=[]
    company=[]
    all_code=[]
    etf_data = []
    
    for i in range(3):
        #if(ETF[i]=='債券型ETF'):continue
        driver.get(request_href[i])  # 替換為目標網址
        # 等待頁面加載完成
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # 確保頁面主要元素加載完成
        # 獲取頁面 HTML
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        href=[]
        while True:
            next_button = driver.find_element("css selector", 'button[aria-label="next"]')
            rows = driver.find_elements(By.CSS_SELECTOR, "table.cm-table__table tbody tr")
            visible_rows = [row for row in rows if row.is_displayed()]
            for tr in visible_rows:
                div = tr.find_element(By.CSS_SELECTOR, "div.text-left.text-multiline")  # 替換為正確的 CSS Selector
                a_tag = div.find_element(By.TAG_NAME, "a")
                temp_href = a_tag.get_attribute("href")
                #print(temp_href)
                href.append(temp_href)  # 保存連結
            if next_button.get_attribute("disabled"):  # 檢查是否有 disabled 屬性
                break
            next_button.click()
            time.sleep(2)  # 等待頁面加載
        for url in href:
            driver.get(url)
            time.sleep(2)  # 等待頁面加載
            # 使用 BeautifulSoup 分析當前頁面的內容
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            #print(soup.find('div', class_="stockMainInfo__title").find('h1'))
            #print(soup.find('div', class_="stockMainInfo__title").find('h1').find('span').text)
            #print(soup.find('span', class_="stockMainInfo__price"))
            #print(soup.find('div', class_="stockMainInfo__summaryItem--body").find("div"))
            try:
                h1 = soup.find('h1', class_='text-2xl')
                name = ''.join(h1.stripped_strings).replace(h1.find('span').text.strip(), '').strip()
                code = soup.find('div', class_="stockMainInfo__title").find('h1').find('span').text.strip()
                price = soup.find('span', class_="stockMainInfo__price").text.replace(" ","").strip()
                start = soup.find('div', class_="stockMainInfo__summaryItem--body").find("div").text.replace("成立時間：","").replace(" ","").strip()
                #print(name, code, price, start)
                if(name in check): 
                    continue
                else:
                    check.append(name)
                #etf_data.append(["債券型ETF", name, code, start, price, "", "", ""])
            except AttributeError:
                print(f"無法從 {url} 提取數據，請檢查 HTML 結構")
            if(code in all_code):
                continue
            else:
                all_code.append(code)
            driver.get("https://www.tdcc.com.tw/portal/zh/smWeb/qryStock")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "StockNo")))
            # 使用 BeautifulSoup 分析當前頁面的內容
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            input_box = driver.find_element(By.ID, "StockNo")
            input_box.send_keys(code)
            search_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="查詢"]')
            search_button.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            tbody = driver.find_element(By.CSS_SELECTOR, "table.table tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            # 獲取最後一行的所有 <td>
            last_row = rows[-1]  # 取最後一行
            columns = last_row.find_elements(By.TAG_NAME, "td")
            people=columns[2].text.strip()
            if(name[0:2] not in company):
                company.append(name[0:2])
            percent,year=get_time(name[0:2],code,name)
            dist=get_data(code)
            if(i==0):
                print(["美國公債",ETF[i], name, code, start, price,people, percent, year,dist['當月配息金額'],dist['當月殖利率'],dist['填息天數'],dist['資產規模'],dist['除息日'],dist['收益分配日'],dist['年初至今總報酬率'],dist['一個月總報酬率'],dist['前一年管理費'],dist['保管銀行']])
                etf_data.append(["美國公債",ETF[i], name, code, start, price,people, percent, year,dist['當月配息金額'],dist['當月殖利率'],dist['填息天數'],dist['資產規模'],dist['除息日'],dist['收益分配日'],dist['年初至今總報酬率'],dist['一個月總報酬率'],dist['前一年管理費'],dist['保管銀行']])
            else:
                print(["非美國公債",ETF[i], name, code, start, price,people, percent, year,dist['當月配息金額'],dist['當月殖利率'],dist['填息天數'],dist['資產規模'],dist['除息日'],dist['收益分配日'],dist['年初至今總報酬率'],dist['一個月總報酬率'],dist['前一年管理費'],dist['保管銀行']])
                etf_data.append(["非美國公債",ETF[i], name, code, start, price,people, percent, year,dist['當月配息金額'],dist['當月殖利率'],dist['填息天數'],dist['資產規模'],dist['除息日'],dist['收益分配日'],dist['年初至今總報酬率'],dist['一個月總報酬率'],dist['前一年管理費'],dist['保管銀行']])
            #print(etf_data)
    print(company)
    return etf_data

# 抓取所有頁面的數據
if __name__ == '__main__':
    all_data = scrape_page_data()
"""
while True:
    all_data.extend(scrape_page_data())
    try:
        # 嘗試點擊下一頁按鈕
        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".next-page-button")))
        next_button.click()
        time.sleep(3)  # 等待新頁面加載
    except:
        print("已到最後一頁")
        break
"""

# 輸出結果
#for row in all_data:
    #print(row)
