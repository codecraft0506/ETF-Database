import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def get_tpex_data(symbol, headless=True):
    # print(f"抓取 TPEX 資料，ETF 代號: {symbol}")
    options = Options()
    if headless:
        options.add_argument("--headless")  # 無頭模式
    driver = webdriver.Firefox(options=options)
    try:
        url = f"https://www.tpex.org.tw/zh-tw/product/etf/product/detail.html?type=bond&code={symbol}"
        driver.get(url)
        # print("已開啟 TPEX 網頁")
        time.sleep(3)  # 等待頁面加載

        # 抓取收益分配日
        dividend_distribution_date = driver.find_element(By.XPATH, '//*[@id="tables-content"]/div[2]/div[2]/table/tbody/tr[21]/td[2]').text.strip()
        # print(f"成功抓取 TPEX 資料，ETF 代號: {symbol}")
    except NoSuchElementException:
        dividend_distribution_date = "-"
    except Exception as e:
        dividend_distribution_date = "Error"
    finally:
        driver.quit()
    
    return {
        "收益分配日": dividend_distribution_date if dividend_distribution_date != "" else "-",
    }

if __name__ == "__main__":
    print(get_tpex_data("00937B", headless=False))
