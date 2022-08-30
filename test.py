import pandas_datareader as pdr
from datetime import date
import pandas as pd

today = date.today()
print(today)
df = pdr.get_data_yahoo('^VIX', '2/12/2016')
if str(today) in df.index:
    df = df.drop(index=today)
dfav=df.head(20)
print(df.index.size)
print(dfav)
print(sum(dfav['Close'])/20)