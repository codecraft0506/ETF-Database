import pandas as pd
from datetime import datetime
from services.yahoo import get_yahoo_data
from services.tpex import get_tpex_data
from services.macromicro import get_macromicro_data
from services.moneydj import get_moneydj_data
from tqdm import tqdm

if __name__ == "__main__":
    from test_symbols import symbols

    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"開始抓取 ETF 資料，日期: {current_date}")
    all_data = []

    for symbol in tqdm(symbols, desc="處理 ETF 代號"):
        yahoo_data = get_yahoo_data(symbol)
        tpex_data = get_tpex_data(symbol)
        macromicro_data = get_macromicro_data(symbol)
        moneydj_data = get_moneydj_data(symbol)

        combined_data = {
            "Date": current_date,
            "Symbol": symbol,
            **yahoo_data,
            **tpex_data,
            **macromicro_data,
            **moneydj_data
        }

        all_data.append(combined_data)

        # 將資料轉換為 DataFrame 並即時寫入 Excel
        df = pd.DataFrame(all_data)
        df.to_excel("output/etf_data.xlsx", index=False)

    print("ETF 資料抓取與匯出完成。")
