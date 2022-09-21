from utils import data_selector as ds
from utils import finance_math as fm

"""
SYSTEM GLOBAL VALUES
"""
DATASETS_SOURCE=""
RSI_TO_BUY=0
RSI_TO_SELL=0
T_SELL=0
T_BUY=0

def initialize_system_global_values():
    global DATASETS_SOURCE, RSI_TO_BUY, RSI_TO_SELL, T_SELL, T_BUY

    DATASETS_SOURCE=ds.get_datasets_source()
    rsi_adjustable=ds.get_data(DATASETS_SOURCE,"RSIADJUST")
    RSI_TO_BUY=float(rsi_adjustable['RSI_TO_BUY'][0])
    RSI_TO_SELL=float(rsi_adjustable['RSI_TO_SELL'][0])
    T_SELL = RSI_TO_SELL-5
    T_BUY = RSI_TO_BUY+5

def main():
    initialize_system_global_values()
    df = ds.get_data(DATASETS_SOURCE,"WATCHLIST")
    print(df)
    print("datasets path: {}".format(DATASETS_SOURCE))
    print("datasets RSI TO BUY: {}".format(RSI_TO_BUY))
    print("datasets RSI TO SELL: {}".format(RSI_TO_SELL))
    print("datasets TO SELL: {}".format(T_SELL))
    print("datasets TO BUY: {}".format(T_BUY))

main()