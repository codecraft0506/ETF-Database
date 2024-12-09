from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_moneydj_data(symbol, headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")  # 無頭模式
    driver = webdriver.Firefox(options=options)
    try:
        url = f"https://www.moneydj.com/ETF/X/Basic/Basic0004.xdjhtm?etfid={symbol}.TW"
        driver.get(url)
        
        # 使用 WebDriverWait 等待元素載入
        wait = WebDriverWait(driver, 10)
        last_year_management_fee = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="sTable"]/tbody/tr[11]/td[1]'))
        ).text.strip()
        
        custodian_bank = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="sTable"]/tbody/tr[15]/td'))
        ).text.strip()
        
    except Exception:
        last_year_management_fee = "Error"
        custodian_bank = "Error"
    finally:
        driver.quit()

    return {
        "前一年管理費": last_year_management_fee if last_year_management_fee != "" else "-",
        "保管銀行": custodian_bank if custodian_bank != "" else "-",
    }

if __name__ == "__main__": 
    print(get_moneydj_data("00937B", headless=False))
