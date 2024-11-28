from scrapling import StealthyFetcher
import time

def get_macromicro_data(symbol, headless=True):
    # print(f"抓取 MacroMicro 資料，ETF 代號: {symbol}")
    try:
        # 初始化 Fetcher 並開啟網頁
        url = f"https://www.macromicro.me/etf/tw/intro/{symbol}"
        fetcher = StealthyFetcher()
        page = fetcher.fetch(url, headless=headless)
        # print("已開啟 MacroMicro 網頁")

        # 檢查並關閉廣告
        try:
            # 等待一段時間以確保廣告出現
            time.sleep(5)
            ad_button = page.xpath('/html/body/div[6]/div/div/nav/button[1]')
            if ad_button:
                ad_button[0].click()
                print("廣告已關閉")
        except Exception as e:
            # print("未檢測到廣告或關閉廣告時發生錯誤")
            pass

        # 確認頁面加載成功
        if page.status == 200:
            # print("頁面加載成功")

            # 抓取年初至今總報酬率和一個月總報酬率
            ytd_total_return = page.xpath('//*[@id="content--price"]/div[3]/div/table/tbody/tr[3]/td[7]')[0].text.strip()
            one_month_total_return = page.xpath('//*[@id="content--price"]/div[3]/div/table/tbody/tr[3]/td[4]')[0].text.strip()
            # print(f"成功抓取 MacroMicro 資料，ETF 代號: {symbol}")
        else:
            # print(f"頁面加載失敗，狀態碼: {page.status}")
            ytd_total_return = "Error"
            one_month_total_return = "Error"
    except Exception as e:
        # print(f"抓取 MacroMicro 資料時發生錯誤，ETF 代號: {symbol}")
        ytd_total_return = "Error"
        one_month_total_return = "Error"

    return {
        "年初至今總報酬率": ytd_total_return,
        "一個月總報酬率": one_month_total_return,
    }

if __name__ == "__main__": 
    print(get_macromicro_data("00844B", headless=False))

