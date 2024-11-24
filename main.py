from scrapling import StealthyFetcher


class StockInfoScraper:
    def __init__(self, symbol):
        self.symbol = symbol
        self.yahoo_base_url = "https://tw.stock.yahoo.com/quote"
        self.macro_micro_base_url = "https://www.macromicro.me/etf/tw/intro"
        self.moneydj_base_url = "https://www.moneydj.com/ETF"
        self.fetcher = StealthyFetcher()

    def fetch_dividend_info(self):
        url = f"{self.yahoo_base_url}/{self.symbol}.TWO/dividend"
        page = self.fetcher.fetch(url)
        
        try:
            dividend_amount = page.css_first(
                '#main-2-QuoteDividend-Proxy section:nth-of-type(2) div:nth-of-type(3) ul li:nth-of-type(2) div:nth-of-type(3) span::text'
            ).clean()
            dividend_yield = page.css_first(
                '#main-2-QuoteDividend-Proxy section:nth-of-type(2) div:nth-of-type(3) ul li:nth-of-type(2) div:nth-of-type(5) span::text'
            ).clean()
            ex_dividend_date = page.css_first(
                '#main-2-QuoteDividend-Proxy section:nth-of-type(2) div:nth-of-type(3) ul li:nth-of-type(2) div:nth-of-type(7)::text'
            ).clean()
            dividend_recovery_days = page.css_first(
                '#main-2-QuoteDividend-Proxy section:nth-of-type(2) div:nth-of-type(3) ul li:nth-of-type(2) div:nth-of-type(11)::text'
            ).clean()
        except AttributeError:
            return {"Error": "無法取得配息資訊，請檢查選擇器或網站結構是否改變。"}
        
        return {
            "MonthlyDividend": dividend_amount,
            "MonthlyDividendYield": dividend_yield,
            "ExDividendDate": ex_dividend_date,
            "DividendRecoveryDays": dividend_recovery_days,
        }

    def fetch_profile_info(self):
        url = f"{self.yahoo_base_url}/{self.symbol}.TWO/profile"
        page = self.fetcher.fetch(url)
        
        try:
            asset_size = page.css_first(
                '#main-2-QuoteProfile-Proxy section:nth-of-type(1) div:nth-of-type(11) div div::text'
            ).clean()
        except AttributeError:
            return {"Error": "無法取得公司概況資訊，請檢查選擇器或網站結構是否改變。"}
        
        return {"AssetSize": asset_size}

    def fetch_yield_info(self):
        url = f"{self.macro_micro_base_url}/{self.symbol}"
        page = self.fetcher.fetch(url)

        try:
            annualized_yield = page.css_first(
                '#content--dividend div:nth-of-type(2) p::text'
            ).clean()
            ytd_total_return = page.css_first(
                '#content--price div:nth-of-type(3) table tbody tr:nth-of-type(3) td:nth-of-type(7)::text'
            ).clean()
            one_month_total_return = page.css_first(
                '#content--price div:nth-of-type(3) table tbody tr:nth-of-type(3) td:nth-of-type(4)::text'
            ).clean()
        except AttributeError:
            return {"Error": "無法取得收益率資訊，請檢查選擇器或網站結構是否改變。"}
        
        return {
            "AnnualizedYield": annualized_yield,
            "YTDTotalReturn": ytd_total_return,
            "OneMonthTotalReturn": one_month_total_return,
        }

    def get_moneydj_info(self):
        url = f"{self.moneydj_base_url}/X/Basic/Basic0004.xdjhtm?etfid={self.symbol}.TW"
        page = self.fetcher.fetch(url)

        try:
            last_year_management_fee = page.css_first(
                '#sTable tbody tr:nth-of-type(11) td:nth-of-type(1)::text'
            ).clean()
            custodian_bank = page.css_first(
                '#sTable tbody tr:nth-of-type(15) td::text'
            ).clean()
        except AttributeError:
            return {"Error": "無法取得 MoneyDJ 資訊，請檢查選擇器或網站結構是否改變。"}
        
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
