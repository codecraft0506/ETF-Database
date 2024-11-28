import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.engines.yahoo import get_yahoo_data
from services.engines.tpex import get_tpex_data
from services.engines.macromicro import get_macromicro_data
from services.engines.moneydj import get_moneydj_data

def get_data(symbol, headless=True):
    yahoo_data = get_yahoo_data(symbol)
    tpex_data = get_tpex_data(symbol, headless)
    macromicro_data = get_macromicro_data(symbol, headless)
    moneydj_data = get_moneydj_data(symbol, headless)

    return {
        **yahoo_data,
        **tpex_data,
        **macromicro_data,
        **moneydj_data
    }

if __name__ == "__main__":
    data = get_data("00844B")
    print(data)

