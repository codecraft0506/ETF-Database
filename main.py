import os
import time
import logging
from datetime import datetime

import requests
from lxml import html
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from scrapling import StealthyFetcher

# ------------------------------
# 設定日誌
# ------------------------------
logging.basicConfig(
    level=logging.INFO,  # 設定日誌等級
    format='%(asctime)s - %(levelname)s - %(message)s',  # 設定日誌格式
    handlers=[
        logging.FileHandler("scraper.log"),  # 寫入日誌檔案
        logging.StreamHandler()  # 同時輸出到控制台
    ]
)

# ------------------------------
# 抓取 Yahoo 資料
# ------------------------------
def get_yahoo_data(symbol):
    logging.info(f"抓取 Yahoo 資料，ETF 代號: {symbol}")
    try:
        dividend_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/dividend"
        dividend_response = requests.get(dividend_url)
        dividend_response.raise_for_status()
        dividend_tree = html.fromstring(dividend_response.text)

        # 抓取配息金額、殖利率、填息天數
        dividend_amount = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[3]/span/text()')
        dividend_yield = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[5]/span/text()')
        dividend_recovery_days = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[11]/text()')

        dividend_amount = dividend_amount[0].strip() if dividend_amount else "N/A"
        dividend_yield = dividend_yield[0].strip() if dividend_yield else "N/A"
        dividend_recovery_days = dividend_recovery_days[0].strip() if dividend_recovery_days else "N/A"

        # 抓取資產規模、除息日
        profile_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/profile"
        profile_response = requests.get(profile_url)
        profile_response.raise_for_status()
        profile_tree = html.fromstring(profile_response.text)

        asset_size = profile_tree.xpath('//*[@id="main-2-QuoteProfile-Proxy"]/div/section[1]/div[2]/div[11]/div/div/text()')
        ex_dividend_date = profile_tree.xpath('//*[@id="main-2-QuoteProfile-Proxy"]/div/section[3]/div[3]/div[3]/div/div/text()')

        asset_size = asset_size[0].strip() if asset_size else "N/A"
        ex_dividend_date = ex_dividend_date[0].strip() if ex_dividend_date else "N/A"

        logging.info(f"成功抓取 Yahoo 資料，ETF 代號: {symbol}")

        return {
            "當月配息金額": dividend_amount,
            "當月殖利率": dividend_yield,
            "填息天數": dividend_recovery_days,
            "資產規模": asset_size,
            "除息日": ex_dividend_date,
        }
    except Exception as e:
        logging.error(f"抓取 Yahoo 資料時發生錯誤，ETF 代號: {symbol}，錯誤訊息: {e}")
        return {
            "當月配息金額": "N/A",
            "當月殖利率": "N/A",
            "填息天數": "N/A",
            "資產規模": "N/A",
            "除息日": "N/A",
        }

# ------------------------------
# 抓取 TPEX 資料
# ------------------------------
def get_tpex_data(symbol, type, driver):
    logging.info(f"抓取 TPEX 資料，ETF 代號: {symbol}")
    try:
        url = f"https://wwwov.tpex.org.tw/web/etf/etf_specification_{type}_detail.php?l=zh-tw&code={symbol}"
        driver.get(url)
        logging.debug("已開啟 TPEX 網頁")
        time.sleep(3)  # 等待頁面加載

        # 抓取收益分配日
        dividend_distribution_date = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[3]/div[2]/table/tbody/tr[21]/td[2]').text.strip()
        logging.info(f"成功抓取 TPEX 資料，ETF 代號: {symbol}")
    except Exception as e:
        logging.error(f"抓取 TPEX 資料時發生錯誤，ETF 代號: {symbol}，錯誤訊息: {e}")
        dividend_distribution_date = "N/A"
    return {
        "收益分配日": dividend_distribution_date,
    }

# ------------------------------
# 抓取 MacroMicro 資料
# ------------------------------
def get_macromicro_data(symbol):
    logging.info(f"抓取 MacroMicro 資料，ETF 代號: {symbol}")
    try:
        # 初始化 Fetcher 並開啟網頁
        url = f"https://www.macromicro.me/etf/tw/intro/{symbol}"
        fetcher = StealthyFetcher()
        page = fetcher.fetch(url, headless=True)
        logging.debug("已開啟 MacroMicro 網頁")

        # 確認頁面加載成功
        if page.status == 200:
            logging.debug("頁面加載成功")

            # 抓取年初至今總報酬率和一個月總報酬率
            ytd_total_return = page.xpath('//*[@id="content--price"]/div[3]/div/table/tbody/tr[3]/td[7]')[0].text.strip()
            one_month_total_return = page.xpath('//*[@id="content--price"]/div[3]/div/table/tbody/tr[3]/td[4]')[0].text.strip()
            logging.info(f"成功抓取 MacroMicro 資料，ETF 代號: {symbol}")
        else:
            logging.error(f"頁面加載失敗，狀態碼: {page.status}")
            ytd_total_return = "N/A"
            one_month_total_return = "N/A"
    except Exception as e:
        logging.error(f"抓取 MacroMicro 資料時發生錯誤，ETF 代號: {symbol}，錯誤訊息: {e}")
        ytd_total_return = "N/A"
        one_month_total_return = "N/A"

    return {
        "年初至今總報酬率": ytd_total_return,
        "一個月總報酬率": one_month_total_return,
    }

# ------------------------------
# 抓取 MoneyDJ 資料
# ------------------------------
def get_moneydj_data(symbol, driver):
    logging.info(f"抓取 MoneyDJ 資料，ETF 代號: {symbol}")
    try:
        url = f"https://www.moneydj.com/ETF/X/Basic/Basic0004.xdjhtm?etfid={symbol}.TW"
        driver.get(url)
        logging.debug("已開啟 MoneyDJ 網頁")
        time.sleep(3)  # 等待頁面加載

        # 抓取前一年管理費和保管銀行
        last_year_management_fee = driver.find_element(By.XPATH, '//*[@id="sTable"]/tbody/tr[11]/td[1]').text.strip()
        custodian_bank = driver.find_element(By.XPATH, '//*[@id="sTable"]/tbody/tr[15]/td').text.strip()
        logging.info(f"成功抓取 MoneyDJ 資料，ETF 代號: {symbol}")
    except Exception as e:
        logging.error(f"抓取 MoneyDJ 資料時發生錯誤，ETF 代號: {symbol}，錯誤訊息: {e}")
        last_year_management_fee = "N/A"
        custodian_bank = "N/A"
    return {
        "前一年管理費": last_year_management_fee,
        "保管銀行": custodian_bank,
    }

# ------------------------------
# 主程式
# ------------------------------
if __name__ == "__main__":
    # 定義 ETF 代號列表
    symbols = ['00687B', '00696B', '00719B']

    # 獲取當前日期
    current_date = datetime.now().strftime("%Y-%m-%d")

    logging.info(f"開始抓取 ETF 資料，日期: {current_date}")

    # 初始化 Selenium WebDriver
    options = Options()
    # options.add_argument("--headless")  # 無頭模式
    driver = webdriver.Firefox(options=options)

    all_data = []

    for symbol in symbols:
        logging.info(f"開始處理 ETF 代號: {symbol}")

        # 抓取各來源資料
        yahoo_data = get_yahoo_data(symbol)
        tpex_data = get_tpex_data(symbol, 'bond', driver)
        macromicro_data = get_macromicro_data(symbol)
        moneydj_data = get_moneydj_data(symbol, driver)

        # 合併資料
        combined_data = {
            "Date": current_date,
            "Symbol": symbol,
            **yahoo_data,
            **tpex_data,
            **macromicro_data,
            **moneydj_data
        }

        logging.debug(f"合併後的資料: {combined_data}")

        all_data.append(combined_data)

    # 關閉 Selenium WebDriver
    driver.quit()

    # 將所有資料轉換為 DataFrame 並寫入 Excel
    df = pd.DataFrame(all_data)
    df.to_excel("etf_data.xlsx", index=False)

    logging.info("ETF 資料抓取與匯出完成。")
