import requests
from lxml import html

def get_yahoo_data(symbol):
    # 抓取配息金額、殖利率、填息天數
    try:
        dividend_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/dividend"
        dividend_response = requests.get(dividend_url, timeout=10)
        dividend_response.raise_for_status()
        dividend_tree = html.fromstring(dividend_response.text)
        dividend_amount = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[3]/span/text()')
        dividend_yield = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[5]/span/text()')
        dividend_recovery_days = dividend_tree.xpath('//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[11]/text()')
        dividend_amount = dividend_amount[0].strip() if dividend_amount else "-"
        dividend_yield = dividend_yield[0].strip() if dividend_yield else "-"
        dividend_recovery_days = dividend_recovery_days[0].strip() if dividend_recovery_days else "-"
    except Exception as e:
        dividend_amount = "Error"
        dividend_yield = "Error"
        dividend_recovery_days = "Error"

    # 抓取資產規模、除息日
    try:
        profile_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/profile"
        profile_response = requests.get(profile_url, timeout=10)
        profile_response.raise_for_status()
        profile_tree = html.fromstring(profile_response.text)
        asset_size = profile_tree.xpath('//*[@id="main-2-QuoteProfile-Proxy"]/div/section[1]/div[2]/div[11]/div/div/text()')
        ex_dividend_date = profile_tree.xpath('//*[@id="main-2-QuoteProfile-Proxy"]/div/section[3]/div[3]/div[3]/div/div/text()')
        asset_size = asset_size[0].strip() if asset_size else "-"
        ex_dividend_date = ex_dividend_date[0].strip() if ex_dividend_date else "-"
    
    except Exception as e:
        asset_size = "Error"
        ex_dividend_date = "Error"
    
    # 抓取年化報酬率
    try:
        return_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TW/performance"
        return_response = requests.get(return_url, timeout=10)
        return_response.raise_for_status()
        return_tree = html.fromstring(return_response.text)
        annual_return = return_tree.xpath('//*[@id="main-2-QuotePerformance-Proxy"]/div/div/div[1]/div[2]/div/div[2]/div/div/ul/li[1]/div/div[2]/span/text()')
        annual_return = annual_return[0].strip() if annual_return else "-"
        
    except Exception as e:
        annual_return = "Error"

    return {
        "當月配息金額": dividend_amount if dividend_amount != "" else "-",
        "當月殖利率": dividend_yield if dividend_yield != "" else "-",
        "填息天數": dividend_recovery_days if dividend_recovery_days != "" else "-",
        "資產規模": asset_size if asset_size != "" else "-",
        "除息日": ex_dividend_date if ex_dividend_date != "" else "-",
        "年化報酬率": annual_return if annual_return != "" else "-",
    }

if __name__ == "__main__":
    print(get_yahoo_data("00678"))
