import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
import numpy as np
d="2016-01-01"
yesterday=np.datetime64('today','D') - np.timedelta64(1,'D')
print(yesterday)
df = yf.Ticker('AA').history(start=d)
print(df)
df = yf.download('AA',start=d)
#df2 = pdr.get_data_yahoo('AA', start=d, end="2022-01-16")
print(df)
#print(df2)