def rsi(comp, options, up_date, stg):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    df = pdr.get_data_yahoo(comp, up_date)
    today = date.today()
    if str(today) in df.index:
        df = df.drop(index=today)
    df.index = df.index.strftime('%m-%d-%Y')
    df.drop(index=df.index[0], 
        axis=0, 
        inplace=True) if df.index.size > 0 else None
    df.drop(['High', 'Low', 'Open', 'Volume', 'Adj Close'], axis=1, inplace=True)

    df = formula1(df)
    df = df.rename(columns={'Close':'Price'})
    df.drop(['delta', 'up', 'down'], axis=1, inplace=True)
    conditions=[df['RSI']<RSI_TO_BUY,df['RSI']>=RSI_TO_BUY] if stg=='A' else [df['RSI']>RSI_TO_SELL,df['RSI']<=RSI_TO_SELL] 

    values = ['BUY', 'HOLD'] if stg=='A' else ['SELL', 'HOLD']

    df['STATUS'] = np.select(conditions, values)
    df=filter_by_options(df,options)
    df['Date']=df.index
    first_column = df.pop('Date')
    df.insert(0,'Date',first_column)
    df = df.reindex(index=df.index[::-1])
    df=eval_gain_loss(df) if stg=='A' else eval_gain_loss_B(df)
    #print(df)
    return df