import pandas as pd
import yfinance as yf
from yfinance import HistoricalPrices
import pandas_datareader as pdr
d="2016-01-01"
df = yf.Ticker('AA').history(start=d)
#df2 = pdr.get_data_yahoo('AA', start=d, end="2022-01-16")
print(df)
#print(df2)