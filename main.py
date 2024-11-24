import requests
from lxml import html

class StockInfoScraper:
    def __init__(self, symbol):
        self.symbol = symbol
        self.yahoo_base_url = "https://tw.stock.yahoo.com/quote"
        self.macro_micro_base_url = "https://www.macromicro.me/etf/tw/intro"
        self.moneydj_base_url = "https://www.moneydj.com/ETF"

    def fetch_dividend_info(self):
        url = f"{self.yahoo_base_url}/{self.symbol}.TWO/dividend"
        response = requests.get(url)
        tree = html.fromstring(response.content)

        try:
            dividend_amount = tree.xpath(
                '//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[3]/span'
            )[0].text_content()
            dividend_yield = tree.xpath(
                '//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[5]/span'
            )[0].text_content()
            ex_dividend_date = tree.xpath(
                '//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[7]'
            )[0].text_content()
            dividend_recovery_days = tree.xpath(
                '//*[@id="main-2-QuoteDividend-Proxy"]/div/section[2]/div[3]/div[2]/div/div/ul/li[2]/div/div[11]'
            )[0].text_content()
        except IndexError:
            return {"Error": "無法取得配息資訊，請檢查 XPath 或網頁結構是否改變。"}

        return {
            "MonthlyDividend": dividend_amount,
            "MonthlyDividendYield": dividend_yield,
            "ExDividendDate": ex_dividend_date,
            "DividendRecoveryDays": dividend_recovery_days,
        }

    def fetch_profile_info(self):
        url = f"{self.yahoo_base_url}/{self.symbol}.TWO/profile"
        response = requests.get(url)
        tree = html.fromstring(response.content)

        try:
            asset_size = tree.xpath(
                '//*[@id="main-2-QuoteProfile-Proxy"]/div/section[1]/div[2]/div[11]/div/div'
            )[0].text_content()
        except IndexError:
            return {"Error": "無法取得公司概況資訊，請檢查 XPath 或網頁結構是否改變。"}

        return {"AssetSize": asset_size}

    def fetch_yield_info(self):
        url = f"{self.macro_micro_base_url}/{self.symbol}"
        response = requests.get(url)
        tree = html.fromstring(response.content)

        # try:
        annualized_yield = tree.xpath(
            '//*[@id="content--dividend"]/div/div[2]/p'
        )
        ytd_total_return = tree.xpath(
            '//*[@id="content--price"]/div[3]/div/table/tbody/tr[3]/td[7]'
        )
        one_month_total_return = tree.xpath(
            '//*[@id="content--price"]/div[3]/div/table/tbody/tr[3]/td[4]'
        )
        # except IndexError:
        #     return {"Error": "無法取得收益率資訊，請檢查 XPath 或網頁結構是否改變。"}

        return {
            "AnnualizedYield": annualized_yield,
            "YTDTotalReturn": ytd_total_return,
            "OneMonthTotalReturn": one_month_total_return,
        }
        
    def get_moneydj_info(self):
        url = f"{self.moneydj_base_url}/X/Basic/Basic0004.xdjhtm?etfid={self.symbol}.TW"
        response = requests.get(url)
        tree = html.fromstring(response.content)
        last_year_management_fee = tree.xpath(
                '//*[@id="sTable"]/tbody/tr[11]/td[1]'
            )[0].text_content()
        custodian_bank = tree.xpath(
                '//*[@id="sTable"]/tbody/tr[15]/td'
            )[0].text_content()
        
        return {
            "LastYearManagementFee": last_year_management_fee,
            "CustodianBank": custodian_bank,
        }


if __name__ == "__main__":
    stock_symbol = "00679B"
    scraper = StockInfoScraper(stock_symbol)

    # 抓取配息資訊
    dividend_info = scraper.fetch_dividend_info()
    print("Dividend Information:", dividend_info)

    # 抓取公司概況資訊
    profile_info = scraper.fetch_profile_info()
    print("Profile Information:", profile_info)

    # 抓取收益率資訊
    yield_info = scraper.fetch_yield_info()
    print("Yield Information:", yield_info)

    # 抓取MoneyDJ資訊
    moneydj_info = scraper.get_moneydj_info()
    print("MoneyDJ Information:", moneydj_info)