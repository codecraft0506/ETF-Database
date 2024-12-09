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
        
        while (len(dividend_recovery_days_list) < 5) and (i < 20):
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
            dividend_amount = dividend_amount_list[0]
            dividend_yield = dividend_yield_list[0]
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
            one_year_dividend_yield = f"{one_year_dividend_yield:.2f}%"
            
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
        "一個月總報酬率": one_month_return,
        "近四季累積配息": one_year_dividend_amount,
        "近四季殖利率": one_year_dividend_yield
    }

if __name__ == "__main__":
    symbols = [
        '0052', '0053', '0055', '00662', '00671R', '00678', '00712', '00714', '00728', '00735', 
        '00737', '00757', '00762', '00770', '00830', '00851', '00861', '00875', '00876', '00877', 
        '00881', '00886', '00887', '00891', '00892', '00895', '00896', '00897', '00898', '00899', 
        '00901', '00902', '00903', '00904', '00908', '00911', '00679B', '00687B', '00694B', '00695B', 
        '00696B', '00697B', '00719B', '00764B', '00768B', '00779B', '00795B', '00847B', '00856B', 
        '00857B', '00859B', '00864B', '00865B', '00931B', '00720B', '00722B', '00723B', '00724B', 
        '00725B', '00734B', '00740B', '00746B', '00749B', '00750B', '00751B', '00754B', '00755B', 
        '00759B', '00761B', '00772B', '00773B', '00775B', '00777B', '00778B', '00780B', '00781B', 
        '00782B', '00785B', '00786B', '00787B', '00788B', '00789B', '00790B', '00791B', '00792B', 
        '00793B', '00799B', '00834B', '00836B', '00840B', '00841B', '00842B', '00844B', '00845B', 
        '00846B', '00853B', '00860B', '00862B', '00863B', '00867B', '00883B', '00890B', '00937B', 
        '00942B', '00711B', '00718B', '00726B', '00756B', '00760B', '00784B', '00794B', '00848B', 
        '00849B', '00870B', '00884B', '00635U', '00642U', '00673R', '00674R', '00693U', '00708L', 
        '00715L', '00738U', '00763U', '00682U', '00683L', '00684R', '00706L', '00707R'
    ]
    for symbol in symbols:
        print(symbol, get_yahoo_data(symbol))
