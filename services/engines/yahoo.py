import requests
from lxml import html

def get_yahoo_data(symbol):
    # dividend
    try:
        dividend_recovery_days_list = []
        dividend_amount_list = []
        dividend_yield_list = []

        dividend_url = f"https://tw.stock.yahoo.com/quote/{symbol}.TWO/dividend"
        dividend_response = requests.get(dividend_url, timeout=10)
        dividend_response.raise_for_status()
        dividend_tree = html.fromstring(dividend_response.text)
        duration = ''
        
        i = 0
        
        while len(dividend_recovery_days_list) <= 12:
            i += 1
            try:
                dividend_recovery_day = dividend_tree.xpath(f'//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[{i}]/div/div[11]/text()')[0].strip()
                if dividend_recovery_day and dividend_recovery_day != '' and dividend_recovery_day != ' ':
                    dividend_recovery_days_list.append(dividend_recovery_day)
                    if duration == '' or duration == 'Error':
                        try:
                            duration_str = dividend_tree.xpath(f'//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[2]/text()')[0].strip()
                            if 'S' in duration_str:
                                duration = 'S'
                            elif 'Q' in duration_str:
                                duration = 'Q'
                            elif 'M' in duration_str:
                                duration = 'M'
                            else:
                                duration = 'Y'
                        except Exception as e:
                            duration = "Error"
                    
                    try:
                        dividend_amount_list.append(dividend_tree.xpath(f'//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[{i}]/div/div[3]/span/text()')[0].strip())
                    except Exception as e:
                        dividend_amount_list.append("Error")
                    try:
                        dividend_yield_list.append(dividend_tree.xpath(f'//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[{i}]/div/div[5]/span/text()')[0].strip())
                    except Exception as e:
                        dividend_yield_list.append("Error")
                        
            except Exception as e:
                continue
        
        if len(dividend_recovery_days_list) == 0:
            dividend_recovery_days = "-"
            dividend_amount = "-"
            dividend_yield = "-"
            one_year_dividend_amount = "-"
            one_year_dividend_yield = "-"
        else:
            dividend_recovery_days = ", ".join(dividend_recovery_days_list[0:4])
            dividend_amount = float(dividend_amount_list[0])
            dividend_yield = float(dividend_yield_list[0].replace('%', ''))
            print(dividend_amount_list[1:13])
            if duration == 'S':
                one_year_dividend_amount = sum(float(amount) for amount in dividend_amount_list[1:3])
                one_year_dividend_yield = sum(float(yield_.replace('%', '')) for yield_ in dividend_yield_list[1:3])
            elif duration == 'Q':
                one_year_dividend_amount = sum(float(amount) for amount in dividend_amount_list[1:5])
                one_year_dividend_yield = sum(float(yield_.replace('%', '')) for yield_ in dividend_yield_list[1:5])
            elif duration == 'M':
                one_year_dividend_amount = sum(float(amount) for amount in dividend_amount_list[1:13])
                one_year_dividend_yield = sum(float(yield_.replace('%', '')) for yield_ in dividend_yield_list[1:13])
            elif duration == 'Y':
                one_year_dividend_amount = float(dividend_amount_list[1])
                one_year_dividend_yield = float(dividend_yield_list[1].replace('%', ''))
            
            dividend_amount = f"{dividend_amount:.3f}"
            dividend_yield = f"{dividend_yield:.1f}%"
            one_year_dividend_amount = f"{one_year_dividend_amount:.3f}"
            one_year_dividend_yield = f"{one_year_dividend_yield:.1f}%"
            
    except Exception as e:
        dividend_recovery_days = "Error"
        dividend_amount = "Error"
        dividend_yield = "Error"
        one_year_dividend_amount = "Error"
        one_year_dividend_yield = "Error"

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
            asset_size = f"{float((asset_size[0].strip()).replace(',', ''))/100:.0f}" if asset_size else "-"
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
            annual_return = f"{float(annual_return[0].strip().replace('%', '')):.1f}%" if annual_return else "-"
        except Exception as e:
            annual_return = "Error"

        # 年初至今總報酬率
        try:
            return_till_today = return_tree.xpath('//*[@id="main-2-QuotePerformance-Proxy"]/div/div/div[1]/div[1]/div/div[2]/div/div/ul/li[5]/div/div[2]/span/text()')
            return_till_today = f"{float(return_till_today[0].strip().replace('%', '')):.1f}%" if return_till_today else "-"
        except Exception as e:
            return_till_today = "Error"
        
        # 一個月總報酬率
        try:
            one_month_return = return_tree.xpath('//*[@id="main-2-QuotePerformance-Proxy"]/div/div/div[1]/div[1]/div/div[2]/div/div/ul/li[2]/div/div[2]/span/text()')
            one_month_return = f"{float(one_month_return[0].strip().replace('%', '')):.1f}%" if one_month_return else "-"
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
        "一個月總報酬率": one_month_return,
        "近四季累積配息": one_year_dividend_amount,
        "近四季殖利率": one_year_dividend_yield
    }

if __name__ == "__main__":
    print(get_yahoo_data("0052"))