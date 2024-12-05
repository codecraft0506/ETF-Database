import requests
from lxml import html

def get_yahoo_data(symbol):
    # dividend
    try:
        dividend_recovery_days = "-"
        dividend_amount = "-"
        dividend_yield = "-"

        dividend_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/dividend"
        dividend_response = requests.get(dividend_url, timeout=10)
        dividend_response.raise_for_status()
        dividend_tree = html.fromstring(dividend_response.text)
        
        dividend_recovery_days = []
        i = 0
        
        while (len(dividend_recovery_days) < 4) and (i < 12):
            i += 1
            try:
                dividend_recovery_day = dividend_tree.xpath(f'//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[{i}]/div/div[11]/text()')
                dividend_recovery_day = dividend_recovery_day[0].strip()
                if dividend_recovery_day and dividend_recovery_day != '' and dividend_recovery_day != ' ':
                    dividend_recovery_days.append(dividend_recovery_day)
                    
                    if len(dividend_recovery_days) == 1:
                        try:
                            dividend_amount = dividend_tree.xpath(f'//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[{i}]/div/div[3]/span/text()')
                            dividend_amount = dividend_amount[0].strip() if dividend_amount else "-"
                        except Exception as e:
                            dividend_amount = "Error"
            
                        try:
                            dividend_yield = dividend_tree.xpath(f'//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[{i}]/div/div[5]/span/text()')
                            dividend_yield = dividend_yield[0].strip() if dividend_yield else "-"
                        except Exception as e:
                            dividend_yield = "Error"
        
            except Exception as e:
                continue
        
        if len(dividend_recovery_days) == 0:
            dividend_recovery_days = "-"
        elif len(dividend_recovery_days) < 4:
            dividend_recovery_days += "(Error: 未滿4次)"
        else:
            dividend_recovery_days = ", ".join(dividend_recovery_days)
            
    except Exception as e:
        dividend_recovery_days = "Error"
        dividend_amount = "Error"
        dividend_yield = "Error"

    # profile
    try:
        asset_size = "-"
        ex_dividend_date = "-"
        
        profile_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/profile"
        profile_response = requests.get(profile_url, timeout=10)
        profile_response.raise_for_status()
        profile_tree = html.fromstring(profile_response.text)
        
        # 資產規模
        try:
            asset_size = profile_tree.xpath('//*[@id="main-2-QuoteProfile-Proxy"]/div/section[1]/div[2]/div[11]/div/div/text()')
            asset_size = asset_size[0].strip() if asset_size else "-"
        except Exception as e:
            asset_size = "Error"
        
        # 除息日
        try:
            ex_dividend_date = profile_tree.xpath('//*[@id="main-2-QuoteProfile-Proxy"]/div/section[3]/div[3]/div[3]/div/div/text()')
            ex_dividend_date = ex_dividend_date[0].strip() if ex_dividend_date else "-"
        except Exception as e:
            ex_dividend_date = "Error"
    
    except Exception as e:
        asset_size = "Error"
        ex_dividend_date = "Error"
    
    # performance
    try:
        annual_return = "-"
        return_till_today = "-"
        one_month_return = "-"
        
        return_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TW/performance"
        return_response = requests.get(return_url, timeout=10)
        return_response.raise_for_status()
        return_tree = html.fromstring(return_response.text)
        
        # 年化報酬率
        try:
            annual_return = return_tree.xpath('//*[@id="main-2-QuotePerformance-Proxy"]/div/div/div[1]/div[2]/div/div[2]/div/div/ul/li[1]/div/div[2]/span/text()')
            annual_return = annual_return[0].strip() if annual_return else "-"
        except Exception as e:
            annual_return = "Error"
        
        # 年初至今總報酬率
        try:
            return_till_today = return_tree.xpath('//*[@id="main-2-QuotePerformance-Proxy"]/div/div/div[1]/div[1]/div/div[2]/div/div/ul/li[5]/div/div[2]/span/text()')
            return_till_today = return_till_today[0].strip() if return_till_today else "-"
        except Exception as e:
            return_till_today = "Error"
        
        # 一個月總報酬率
        try:
            one_month_return = return_tree.xpath('//*[@id="main-2-QuotePerformance-Proxy"]/div/div/div[1]/div[1]/div/div[2]/div/div/ul/li[2]/div/div[2]/span/text()')
            one_month_return = one_month_return[0].strip() if one_month_return else "-"
        except Exception as e:
            one_month_return = "Error"
        
    except Exception as e:
        annual_return = "Error"
        return_till_today = "Error"
        one_month_return = "Error"

    return {
        "當月配息金額": dividend_amount,
        "當月殖利率": dividend_yield,
        "填息天數(遠-近)": dividend_recovery_days,
        "資產規模": asset_size,
        "除息日": ex_dividend_date,
        "年化報酬率": annual_return,
        "年初至今總報酬率": return_till_today,
        "一個月總報酬率": one_month_return
    }

if __name__ == "__main__":
    print(get_yahoo_data("00662"))
