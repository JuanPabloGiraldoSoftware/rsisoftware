import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
import numpy as np
d="2016-01-01"
yesterday=np.datetime64('today','D') - np.timedelta64(1,'D')
pd.options.display.float_format = '{:,.2f}'.format
today=np.datetime64('today','D')
print(today)

stocks = ['AA', 'AAL', 'AAPL', 'ABT', 'ADM', 'AEE', 'AEO', 'AFL', 'AIG', 'AIR', 'ALL', 'AMD', 'AMRK', 'AMZN', 'AOS', 'APA', 'APH', 'ARKK', 'AXP', 'AZN']
bolsa=[]
calendario={}
for y in range(2016,int(str(today).split('-')[0]),1):
    for m in range(1,13,1):
        for d in range(1,32):
            calendario[f'{y}-{m}-{d}']=[]

df_total=[]
for s in stocks:
    df = yf.download(stocks[1],start=d)
    df['D%Change'] = df['Close'].pct_change()*100
    df['Datecol'] = df.index
    df['YTD%Change'] = df[df['Datecol']>'2023-01-01']['Close'].transform(lambda x: x/x.iloc[0]-1.0)*100
    df['Year'] = df['Datecol'].apply(lambda x : x.year)
    df=df.loc[df.groupby(pd.Grouper(key='Datecol', freq='1M')).Datecol.idxmin()]
    df['Month']=df['Datecol'].apply(lambda x : x.month)
    df['Stock']=s
    df_tmp=df[df['Close']>32]
    df_tmp=df_tmp.drop(['Open','High','Low','Close','Adj Close', 'Volume', 'D%Change', 'YTD%Change', 'Year', 'Month'], axis=1)
    if len(df_total)==0:
        df_total=df_tmp
    else:
        df_total=pd.concat([df_total,df_tmp])
    print(df_total)
    bolsa.append(df)

df_total['Stocks']=df_total.groupby([df_total['Datecol'].dt.date])['Stock'].count()
print(df_total.drop(['Stock'],axis=1))

def count_stocks(lim,rel,date):
    if rel=='>':
        for df in bolsa:
            for d in calendario.keys():
                df_tmp=df[df['Datecol']==d]
                if len(df_tmp['Close'])>0 and df_tmp['Close'][0]>lim:
                    calendario[d].append((df_tmp['Close'][0],df_tmp['Stock'][0]))
                #calendario[d].append(df['Close'],df['Stock'])           
    elif rel=='<':
        return

def printc(calendar):
    for d in calendar.keys():
        if len(calendar[d]) > 0:
            print(calendar[d])

ths=10
count_stocks(ths,'>','')
for d in calendario.keys():
    stinvolved=set()
    for v in calendario[d]:
        stinvolved.add(v[1])
    if len(calendario[d])>0:
        calendario[d]=[len(calendario[d]),list(stinvolved),d]

cols={'Count':[],'Stocks':[],'Date':[], 'Threshold':[]}

for d in calendario.keys():
    vals=calendario[d]
    if len(vals)==3:
        cols['Count'].append(vals[0])
        stocks_str=''
        for s in vals[1]:
            stocks_str+=s+', '
        cols['Stocks'].append(stocks_str.strip())
        cols['Date'].append(vals[2])
        cols['Threshold'].append(f'> {ths}')

df_final=pd.DataFrame(cols)