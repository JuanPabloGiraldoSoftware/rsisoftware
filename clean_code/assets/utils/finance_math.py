import pandas as pd
import numpy as np
import yfinance as yf

def formula1(df):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    df['delta'] = delta = df['Close'].diff()
    df['up'] = up = delta.clip(lower=0)
    df['down'] = down = -1*delta.clip(upper=0)

    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()

    rs= ema_up/ema_down
    df['RSI'] = round(100 - (100/(1+rs)),2)
    return df

def rsi(comp, options, up_date, chy):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    print(comp, up_date)
    df=None
    if chy:
        yesterday=np.datetime64('today','D')
        df = yf.download(comp, start=up_date, end=str(yesterday))
    else:
        df = yf.download(comp, start=up_date)
    df.index = df.index.strftime('%m-%d-%Y')
    df.drop(['High', 'Low', 'Open', 'Volume','Adj Close'], axis=1, inplace=True)
    df = formula1(df)
    df = df.rename(columns={'Close':'Price'})
    df.drop(['delta', 'up', 'down'], axis=1, inplace=True)
    conditions=[df['RSI']<RSI_TO_BUY, df['RSI']>RSI_TO_SELL,(df['RSI']>=RSI_TO_BUY) & (df['RSI']<=RSI_TO_SELL)] 
    values = ['BUY', 'SELL', 'HOLD'] 
    df['STATUS'] = np.select(conditions, values)
    df=filter_by_options(df,options)
    df['Date']=df.index
    first_column = df.pop('Date')
    df.insert(0,'Date',first_column)
    df = df.reindex(index=df.index[::-1])
    return df