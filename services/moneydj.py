import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

def get_moneydj_data(symbol, headless=True):
    # print(f"抓取 MoneyDJ 資料，ETF 代號: {symbol}")
    options = Options()
    if headless:
        options.add_argument("--headless")  # 無頭模式
    driver = webdriver.Firefox(options=options)
    try:
        url = f"https://www.moneydj.com/ETF/X/Basic/Basic0004.xdjhtm?etfid={symbol}.TW"
        driver.get(url)
        # print("已開啟 MoneyDJ 網頁")
        time.sleep(3)  # 等待頁面加載

        # 抓取前一年管理費和保管銀行
        last_year_management_fee = driver.find_element(By.XPATH, '//*[@id="sTable"]/tbody/tr[11]/td[1]').text.strip()
        custodian_bank = driver.find_element(By.XPATH, '//*[@id="sTable"]/tbody/tr[15]/td').text.strip()
        # print(f"成功抓取 MoneyDJ 資料，ETF 代號: {symbol}")
    except Exception as e:
        # print(f"抓取 MoneyDJ 資料時發生錯誤，ETF 代號: {symbol}")
        last_year_management_fee = "Error"
        custodian_bank = "Error"
    finally:
        driver.quit()

    return {
        "前一年管理費": last_year_management_fee,
        "保管銀行": custodian_bank,
    }

if __name__ == "__main__": 
    print(get_moneydj_data("00635U", headless=False))

