import requests
from lxml import html

def get_yahoo_data(symbol):
    # print(f"抓取 Yahoo 資料，ETF 代號: {symbol}")
    try:
        dividend_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/dividend"
        dividend_response = requests.get(dividend_url)
        dividend_response.raise_for_status()
        dividend_tree = html.fromstring(dividend_response.text)

        # 抓取配息金額、殖利率、填息天數
        dividend_amount = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[3]/span/text()')
        dividend_yield = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[5]/span/text()')
        dividend_recovery_days = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[11]/text()')

        dividend_amount = dividend_amount[0].strip() if dividend_amount else "-"
        dividend_yield = dividend_yield[0].strip() if dividend_yield else "-"
        dividend_recovery_days = dividend_recovery_days[0].strip() if dividend_recovery_days else "-"

        # 抓取資產規模、除息日
        profile_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/profile"
        profile_response = requests.get(profile_url)
        profile_response.raise_for_status()
        profile_tree = html.fromstring(profile_response.text)

        asset_size = profile_tree.xpath('//*[@id="main-2-QuoteProfile-Proxy"]/div/section[1]/div[2]/div[11]/div/div/text()')
        ex_dividend_date = profile_tree.xpath('//*[@id="main-2-QuoteProfile-Proxy"]/div/section[3]/div[3]/div[3]/div/div/text()')

        asset_size = asset_size[0].strip() if asset_size else "-"
        ex_dividend_date = ex_dividend_date[0].strip() if ex_dividend_date else "-"

        # print(f"成功抓取 Yahoo 資料，ETF 代號: {symbol}")

        return {
            "當月配息金額": dividend_amount,
            "當月殖利率": dividend_yield,
            "填息天數": dividend_recovery_days,
            "資產規模": asset_size,
            "除息日": ex_dividend_date,
        }
    except Exception as e:
        # print(f"抓取 Yahoo 資料時發生錯誤，ETF 代號: {symbol}")
        return {
            "當月配息金額": "Error",
            "當月殖利率": "Error",
            "填息天數": "Error",
            "資產規模": "Error",
            "除息日": "Error",
        }
    
if __name__ == "__main__":
    print(get_yahoo_data("00678"))
