import pandas as pd
import pathlib
import yfinance as yf

source=pathlib.Path(__file__).parent.resolve()

def get_symbols():
    df = pd.read_csv(f"{source}/../data_files/STOCKS.csv")
    symbols=list(df['0'])
    return symbols

def get_dataframe(symbol):
    df = pd.read_csv(f'{source}/../data_files/{symbol}.csv')
    return df

def get_table_conditional():
    df=pd.read_csv(f"{source}/../data_files/RSIADJUST.csv")
    RSI_TO_BUY=float(df['RSI_TO_BUY'][0])
    RSI_TO_SELL=float(df['RSI_TO_SELL'][0])
    print(RSI_TO_BUY,RSI_TO_SELL)
    T_BUY=RSI_TO_BUY+5
    T_SELL=RSI_TO_SELL-5
    return '({RSI} >='+str(RSI_TO_BUY)+' && {RSI}<='+str(T_BUY)+') || ({RSI}>='+str(T_SELL)+' && {RSI}<='+str(RSI_TO_SELL)+')'

def pull_finance_data(symbol, yest, up_date):
    df = None
    if yest:
        yesterday=np.datetime64('today','D')
        df = yf.download(symbol, start=up_date, end=str(yesterday))
    else:
        df = yf.download(symbol, start=up_date)
    return df