from posixpath import split
import dash
from dash import Dash, dash_table, Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas_datareader as pdr
import yfinance as yf
import pandas as pd
import datetime as dt
from datetime import date
import numpy as np
import pathlib
import webbrowser 
import math 
import os
from flask import request
from dash.dash_table.Format import Format, Scheme, Trim

yf.pdr_override()
pd.options.display.float_format = '{:,.2f}'.format
app=dash.Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.JOURNAL],
    meta_tags=[{'name':'viewport',
    'content':'width=divice-width, initial-scale=1.0'
    }])

source_adj=pathlib.Path(__file__).parent.resolve()
rsi_adjustable=pd.read_csv('{0}/data_base/RSIADJUST.csv'.format(source_adj))
RSI_TO_BUY=float(rsi_adjustable['RSI_TO_BUY'][0])
RSI_TO_SELL=float(rsi_adjustable['RSI_TO_SELL'][0])
T_SELL = RSI_TO_SELL-5
T_BUY = RSI_TO_BUY+5
companies = []
click_counter = [0,0,0,0]
source=pathlib.Path(__file__).parent.resolve()
df=pd.read_csv('{0}/data_base/STOCKS.csv'.format(source))
for stock in df.values:
    companies.append(stock[0])
companies = list(set(companies))
companies.sort()

@app.callback(
    [Output('dashboard-header','children'),Output('dashboard-content','children'),
    Output('mdpage','n_clicks'),Output('wl1page','n_clicks'),Output('wl2page','n_clicks')],
    [Input('mdpage','n_clicks'), Input('wl1page','n_clicks'), Input('wl2page','n_clicks')]
)
def change_dashboard_page(clicks_md, clicks_wl1, clicks_wl2):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    source=pathlib.Path(__file__).parent.resolve()
    df=pd.read_csv('{0}/data_base/AA.csv'.format(source))
    df = filter_by_options(df,[True,True,True])
    if clicks_wl1:
        df=pd.read_csv('{0}/data_base/WATCHLIST.csv'.format(source))
        df = filter_by_options(df,[True,True,True])
        wl_df=[]
        for stock in companies:
            df_tmp = df[df['Stock']==stock].head(1)
            if len(wl_df)==0:
                wl_df=df_tmp
            else:
                wl_df=pd.concat([wl_df,df_tmp])
        df=wl_df
        return watchlist1_dashboard(), render_wl1_table(df),0,0,0
    elif clicks_wl2:
        df=pd.read_csv('{0}/data_base/WATCHLIST2.csv'.format(source))
        df = filter_by_options(df,[True,True,True])
        return watchlist2_dashboard(), render_wl2_table(df),0,0,0
    return main_dashboard_header(), render_table(df),0,0,0

@app.callback(
    [Output('fakeOutputTest','children'), Output('company-filter', 'options'), Output('remove-dropdown-menu','options'), 
    Output('input-stock-symbol','value'), Output('remove-dropdown-menu','value')],
    [Input('add-data','n_clicks'), Input('remove-data','n_clicks'), Input('add-date-picker','date')],
    [ State('input-stock-symbol','value'), State('remove-dropdown-menu','value')]
)

def remove_or_add_new_stock(add, remove, add_date, stock_to_add,stock_to_remove):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    global companies
    print(click_counter, remove)
    fake=html.Div()
    if add>click_counter[1] and len(stock_to_add)>0:
        click_counter[1]=add
        print('adding stock')
        try:
            stock=stock_to_add.upper()
            if stock in companies:
                raise Exception('That stock already exists')
            df = []
            df=rsi(stock,[True,True,True], add_date, False)
            companies.append(stock)
            companies.sort()
            source=pathlib.Path(__file__).parent.resolve()
            df.to_csv('{0}/data_base/{1}.csv'.format(source, stock), index=False, float_format='%.2f')
            df = pd.DataFrame(companies)
            source=pathlib.Path(__file__).parent.resolve()
            df.to_csv('{0}/data_base/STOCKS.csv'.format(source), index=False)

        except Exception as e:
            print(type(e))
            print(pdr._utils.RemoteDataError)
            if type(e) == pdr._utils.RemoteDataError:
                fake=dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Error Fetching Data")),
                        dbc.ModalBody("We could not find any data related to that symbol."),
                        dbc.ModalFooter(),
                    ],
                    id="error-modal",
                    is_open=True,
                )
            else:
                fake=dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Existing Stock")),
                        dbc.ModalBody(str(e)),
                        dbc.ModalFooter(),
                    ],
                    id="error-modal",
                    is_open=True,
                )   
    elif remove>click_counter[0] and len(stock_to_remove)>0:
        click_counter[0]=remove
        companies.remove(stock_to_remove)
        source=pathlib.Path(__file__).parent.resolve()
        os.remove('{0}/data_base/{1}.csv'.format(source, stock_to_remove))
        companies.sort()
        df= pd.DataFrame(companies)
        df.to_csv('{0}/data_base/STOCKS.csv'.format(source), index=False)
    return fake, companies , companies,'', ''

@app.callback(
    Output('remove-modal','is_open'),
    [Input("remove-stock","n_clicks"), Input('close-remove','n_clicks'), Input('remove-data','n_clicks')],
    [State('remove-modal','is_open')]
)
def toggle_remove_modal(open_modal,close_modal, remove_button,is_open):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    if open_modal or close_modal or remove_button>click_counter[0]:
        print(remove_button)
        click_counter[0] = remove_button
        return not is_open
    return is_open

@app.callback(
    Output('add-modal','is_open'),
    [Input("add-new-stock","n_clicks"), Input('close-add','n_clicks'), Input('add-data','n_clicks')],
    [State('add-modal','is_open')]
)
def toggle_add_modal(open_modal,close_modal, add_button,is_open):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    if open_modal or close_modal or add_button>click_counter[1]:
        print(add_button)
        click_counter[1]=add_button
        return not is_open
    return is_open

@app.callback(
Output('fakeOutputAdjust', 'children'),
Input('adjust-data','n_clicks'), Input('rssell', 'value'), Input('rsbuy','value')
)
def adjust_rsi(n_clicks, rsell,rbuy):
    global companies, RSI_TO_BUY, RSI_TO_SELL, T_SELL, T_BUY
    print('inadjust')
    if n_clicks>click_counter[3]:
        print('entering conditional')
        click_counter[3]=n_clicks
        source=pathlib.Path(__file__).parent.resolve()
        df_rs=pd.read_csv('{0}/data_base/RSIADJUST.csv'.format(source))
        df_rs['RSI_TO_BUY'] = rbuy
        df_rs['RSI_TO_SELL'] = rsell
        print(df_rs)
        df_rs.to_csv('{0}/data_base/RSIADJUST.csv'.format(source), index=False, float_format='%.2f')
        RSI_TO_BUY=float(rbuy)
        RSI_TO_SELL=float(rsell)
        T_SELL = RSI_TO_SELL-5
        T_BUY = RSI_TO_BUY+5
        counter = 1
        size = len(companies)
        tmp_companies=companies+['WATCHLIST','WATCHLIST2']
        df_watchlist=[]
        df_watchlist2=[]
        max_date = None
        for symbol in tmp_companies:
            progress=round((counter/size)*100, 2)
            print('{0}% updating {1} data...'.format(str(progress),symbol))
            df=pd.read_csv('{0}/data_base/{1}.csv'.format(source, symbol))
            if max_date == None:
                max_date=df['Date'].head(1)[0]
            else:
                max_date = max(max_date,df['Date'].head(1)[0])
            conditions=[
                df['RSI']<RSI_TO_BUY, 
                df['RSI']>RSI_TO_SELL,
                (df['RSI']>=RSI_TO_BUY) & (df['RSI']<=RSI_TO_SELL)]
            values = ['BUY', 'SELL', 'HOLD']
            df['STATUS'] = np.select(conditions, values)
            df.to_csv('{0}/data_base/{1}.csv'.format(source, symbol), index=False, float_format='%.2f')
            dftmp = df[(df['RSI'] <= T_BUY) & (df['RSI']>=RSI_TO_BUY) | ((df['RSI']<=RSI_TO_SELL) & (df['RSI']>=T_SELL))]
            dftmp2 = df[df['STATUS']!='HOLD'] 
            if len(df_watchlist) == 0:
                print('{0}% updating {1} data...'.format(str(progress),'WATCHLIST'))
                df_watchlist = dftmp
                df_watchlist2 = dftmp2
            else:
                print('{0}% updating {1} data...'.format(str(progress),'WATCHLIST'))
                df_watchlist=pd.concat([df_watchlist,dftmp])
                df_watchlist2=pd.concat([df_watchlist2,dftmp2])
            counter+=1
        df_watchlist = df_watchlist[df_watchlist['Date']==max_date]
        df_watchlist2 = df_watchlist2[df_watchlist2['Date']==max_date]
        df_watchlist.to_csv('{0}/data_base/WATCHLIST.csv'.format(source), index=False, float_format='%.2f')
        df_watchlist2.to_csv('{0}/data_base/WATCHLIST2.csv'.format(source), index=False, float_format='%.2f')
            
    return html.Div([])

@app.callback(
    Output('adjust-modal','is_open'),
    [Input("adjust-data-button","n_clicks"), Input('close_adjust','n_clicks'), Input('adjust-data','n_clicks')],
    [State('adjust-modal','is_open')]
)
def toggle_modal_adjust(open_modal,close_modal,adj_modal, is_open):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    print('active adjust')
    if open_modal or close_modal or adj_modal>click_counter[3]:
        click_counter[3]=adj_modal
        return not is_open
    return is_open


@app.callback(
Output('fakeOutput', 'children'),
Input('update-data','n_clicks'), Input('update-date-picker', 'date'), Input('check-yesterday','value')
)
def update_data_base(n_clicks, up_date,check_yesterday):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL, companies
    print(date)
    if n_clicks>click_counter[2]:
        click_counter[2]=n_clicks
        df_watchlist=[]
        df_watchlist2=[]
        counter=1
        size=len(companies)
        max_date=None
        print("Value: {}".format(check_yesterday))
        for symbol in companies:
            progress=round((counter/size)*100, 2)
            print('{0}% updating {1} data...'.format(str(progress),symbol))
            df = rsi(symbol,[True,True,True], up_date, check_yesterday)
            if max_date == None:
                max_date=df['Date'].head(1)[0]
            else:
                max_date = max(max_date,df['Date'].head(1)[0])
            print(max_date)
            source=pathlib.Path(__file__).parent.resolve()
            df.to_csv('{0}/data_base/{1}.csv'.format(source, symbol), index=False, float_format='%.2f')
            df['Stock'] = symbol
            dftmp = df[(df['RSI'] <= T_BUY) & (df['RSI']>=RSI_TO_BUY) | ((df['RSI']<=RSI_TO_SELL) & (df['RSI']>=T_SELL))]
            dftmp2 = df[df['STATUS']!='HOLD']
            if len(df_watchlist) == 0:
                print('{0}% updating {1} data...'.format(str(progress),'WATCHLIST'))
                df_watchlist = dftmp
                df_watchlist2 = dftmp2
            else:
                print('{0}% updating {1} data...'.format(str(progress),'WATCHLIST'))
                df_watchlist=pd.concat([df_watchlist,dftmp])
                df_watchlist2=pd.concat([df_watchlist2,dftmp2])
            counter+=1
        df_watchlist = df_watchlist[df_watchlist['Date']==max_date]
        df_watchlist2 = df_watchlist2[df_watchlist2['Date']==max_date]
        df_watchlist.to_csv('{0}/data_base/WATCHLIST.csv'.format(source), index=False, float_format='%.2f')
        df_watchlist2.to_csv('{0}/data_base/WATCHLIST2.csv'.format(source), index=False, float_format='%.2f')
    return html.Div([])


@app.callback(
    [Output("watchlist2_Table","data"), Output("watchlist2_Table","columns"), Output('wl2_title_T','children')],
    [
        Input("wl2_company-filter", "value"),
    ]
)
def update_wl2_table(comp):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    print(comp)
    source=pathlib.Path(__file__).parent.resolve()
    df=pd.read_csv('{0}/data_base/WATCHLIST2.csv'.format(source))
    df = filter_by_options(df,[True,True,True])
    wl_df = []
    for stock in companies:
        df_tmp = df[df['Stock']==stock].head(1)
        if len(wl_df)==0:
            wl_df=df_tmp
        else:
            wl_df=pd.concat([wl_df,df_tmp])
    df=wl_df
    if 'WATCHLIST2'!=comp:
        df=df[df['Stock']==comp]
    rsi_records_data=df.to_dict('records')
    rsi_values_columns=[{"name": i, "id": i,'type':'numeric', 'format':Format(precision=2,scheme=Scheme.fixed)} if i =='RSI' or i=='Price' else 
            {"name": i, "id": i}for i in df.columns]
    return rsi_records_data, rsi_values_columns, comp

@app.callback(
    [Output("watchlist1_Table","data"), Output("watchlist1_Table","columns"), Output('wl1_title_T','children')],
    [
        Input("wl1_company-filter", "value"),
    ]
)
def update_wl1_table(comp):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    print(comp)
    source=pathlib.Path(__file__).parent.resolve()
    df=pd.read_csv('{0}/data_base/WATCHLIST.csv'.format(source))
    df = filter_by_options(df,[True,True,True])
    wl_df = []
    for stock in companies:
        df_tmp = df[df['Stock']==stock].head(1)
        if len(wl_df)==0:
            wl_df=df_tmp
        else:
            wl_df=pd.concat([wl_df,df_tmp])
    df=wl_df
    if 'WATCHLIST'!=comp:
        df=df[df['Stock']==comp]
    rsi_records_data=df.to_dict('records')
    rsi_values_columns=[{"name": i, "id": i,'type':'numeric', 'format':Format(precision=2,scheme=Scheme.fixed)} if i =='RSI' or i=='Price' else 
            {"name": i, "id": i}for i in df.columns]
    return rsi_records_data, rsi_values_columns, comp



@app.callback(
    [Output("rsi_Table","data"), Output("rsi_Table","columns"), Output('title_T','children')],
    [
        Input("company-filter", "value"),
        Input('options-checkbox','value')
    ]
)
def update_table(comp, options):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    outops = [False for i in range(3)]
    for o in options:
        outops[o-1] = True
    source=pathlib.Path(__file__).parent.resolve()
    df=pd.read_csv('{0}/data_base/{1}.csv'.format(source, comp))
    df = filter_by_options(df,outops)
    rsi_records_data=df.to_dict('records')
    rsi_values_columns=[{"name": i, "id": i,'type':'numeric', 'format':Format(precision=2,scheme=Scheme.fixed)} if i =='RSI' or i=='Price' else 
            {"name": i, "id": i}for i in df.columns]
    return rsi_records_data, rsi_values_columns, comp

@app.callback(
    Output('update-modal','is_open'),
    [Input("update-data-button","n_clicks"), Input('close','n_clicks'), Input('update-data','n_clicks')],
    [State('update-modal','is_open')]
)
def toggle_modal(open_modal,close_modal,up_modal, is_open):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    print('active')
    if open_modal or close_modal or up_modal>click_counter[2]:
        click_counter[2]=up_modal
        return not is_open
    return is_open

def filter_by_options(df,options):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    compare_ops=[]
    if options[0] and options[1] and options [2]:
        pass
    elif options[0] and options[1]:
        compare_ops=['SELL', 'BUY']
    elif options[0] and options[2]:
        compare_ops=['SELL', 'HOLD']
    elif options[1] and options[2]:
        compare_ops=['BUY', 'HOLD']
    elif options[0]:
        compare_ops=['SELL']
    elif options[1]:
        compare_ops=['BUY']
    elif options[2]:
        compare_ops=['HOLD']
    if len(compare_ops) == 2:
        df = df[(df['STATUS']==compare_ops[0]) | (df['STATUS']==compare_ops[1])]
    elif len(compare_ops) ==1:
        df = df[(df['STATUS']==compare_ops[0])]
    return df

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

def render_modal_remove():
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    return html.Div(
    [dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Delete Stock")),
                dbc.ModalBody(
                    render_dropdown_menu(companies,'remove-dropdown-menu',""),
                ),
                dbc.ModalFooter([
                    dbc.Button(
                        "Remove", id="remove-data", className="ms-auto", n_clicks=0
                    ),
                    dbc.Button(
                        "Cancel", id="close-remove", className="ms-auto", n_clicks=0
                    )
            ]),
            ],
            id="remove-modal",
            is_open=False,
        ),])

def render_modal_add():
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    return html.Div(
    [dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Add New Stock")),
                dbc.ModalBody(
                    dbc.Input(id="input-stock-symbol", placeholder="Type stock symbol", type="text"),
                ),
                dcc.DatePickerSingle(
                    id='add-date-picker',
                    min_date_allowed=date(2020, 1, 1),
                    initial_visible_month=date(2020, 1, 1),
                    date=date(2020, 1, 1),
                    with_portal=True
                ),
                dbc.ModalFooter([
                    dbc.Button(
                        "Add", id="add-data", className="ms-auto", n_clicks=0
                    ),
                    dbc.Button(
                        "Cancel", id="close-add", className="ms-auto", n_clicks=0
                    )
            ]),
            ],
            id="add-modal",
            is_open=False,
        ),])

def render_modal_adjust():
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    source=pathlib.Path(__file__).parent.resolve()
    df=pd.read_csv('{0}/data_base/RSIADJUST.csv'.format(source))
    br,sr = df.values[0]
    return html.Div(
    [dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Adjust RSI")),
                dcc.Input(
                    id="rssell", type="number",
                    debounce=True, placeholder="RSI Sell Ceil (Current: {})".format(sr),
                ),
                dcc.Input(
                    id="rsbuy", type="number",
                    debounce=True, placeholder="RSI Buy Floor (Current: {})".format(br),
                ),
                dbc.ModalFooter([
                    dbc.Button(
                        "Adjust", id="adjust-data", className="ms-auto", n_clicks=0
                    ),
                    dbc.Button(
                        "Cancel", id="close_adjust", className="ms-auto", n_clicks=0
                    )
            ]),
            ],
            id="adjust-modal",
            is_open=False,
        ),])

def render_modal_update():
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    return html.Div(
    [dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Warning")),
                dbc.ModalBody("Do you really want to update the data base? this action cannot be undone!!"),
                dbc.Row(children=[
                    dbc.Col(dcc.DatePickerSingle(
                        id='update-date-picker',
                        min_date_allowed=date(2016, 1, 1),
                        initial_visible_month=date(2016, 1, 1),
                        date=date(2016, 1, 1),
                        with_portal=True
                    )),
                    dbc.Col(dcc.Checklist(
                        ['Update until yesterday'],
                        id='check-yesterday'
                    ))]
                ),
                dbc.ModalFooter([
                    dbc.Button(
                        "Update", id="update-data", className="ms-auto", n_clicks=0
                    ),
                    dbc.Button(
                        "Cancel", id="close", className="ms-auto", n_clicks=0
                    )
            ]),
            ],
            id="update-modal",
            is_open=False,
        ),])

def render_table(df):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    print("alskakdlk",RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL)
    render_conditional = '({RSI} >='+str(RSI_TO_BUY)+' && {RSI}<='+str(T_BUY)+') || ({RSI}>='+str(T_SELL)+' && {RSI}<='+str(RSI_TO_SELL)+')'
    return [
            dash_table.DataTable(data=df.to_dict('records'), 
            columns=[{"name": i, "id": i,'type':'numeric', 'format':Format(precision=2,scheme=Scheme.fixed)} if i =='RSI' or i=='Price' else 
            {"name": i, "id": i}for i in df.columns],
            id='rsi_Table',
            page_size=25,
            style_header={'textAlign': 'center',
                        'color':'white',
                        'background-color':'#02457a',
                        'font-size':'16px'},
            style_cell={'textAlign': 'left',
                        'color':'black',
                        'font-size':'13px'},
            style_data_conditional=[
                {
                    'if': {
                        'filter_query':render_conditional,
                        'column_id': 'RSI'
                        },
                    'background-color': 'yellow',
                },
                {
                    'if': {
                        'filter_query':render_conditional,
                        'column_id': 'STATUS'
                        },
                    'background-color': 'yellow',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('SELL'),
                        'column_id': 'RSI'
                        },
                    'background-color': 'red',                 
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('SELL'),
                        'column_id': 'STATUS'
                        },
                    'background-color': 'red',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('BUY'),
                        'column_id': 'RSI'
                        },
                    'background-color': 'green',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('BUY'),
                        'column_id': 'STATUS'
                        },
                    'background-color': 'green',
                },
                {
                    'if': {
                        'column_id': 'Price'
                        },
                    'text-align': 'right',
                },
                                {
                    'if': {
                        'column_id': 'RSI'
                        },
                    'text-align': 'right',
                }
            ])]

def render_wl1_table(df):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    render_conditional = '({RSI} >='+str(RSI_TO_BUY)+' && {RSI}<='+str(T_BUY)+') || ({RSI}>='+str(T_SELL)+' && {RSI}<='+str(RSI_TO_SELL)+')'
    return [
            dash_table.DataTable(data=df.to_dict('records'), 
            columns=[{"name": i, "id": i,'type':'numeric', 'format':Format(precision=2,scheme=Scheme.fixed)} if i =='RSI' or i=='Price' else 
            {"name": i, "id": i}for i in df.columns],
            id='watchlist1_Table',
            page_size=25,
            style_header={'textAlign': 'center',
                        'color':'white',
                        'background-color':'#02457a',
                        'font-size':'16px'},
            style_cell={'textAlign': 'left',
                        'color':'black',
                        'font-size':'13px'},
            style_data_conditional=[
                {
                    'if': {
                        'filter_query':render_conditional,
                        'column_id': 'RSI'
                        },
                    'background-color': 'yellow',
                },
                {
                    'if': {
                        'filter_query':render_conditional,
                        'column_id': 'STATUS'
                        },
                    'background-color': 'yellow',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('SELL'),
                        'column_id': 'RSI'
                        },
                    'background-color': 'red',                 
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('SELL'),
                        'column_id': 'STATUS'
                        },
                    'background-color': 'red',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('BUY'),
                        'column_id': 'RSI'
                        },
                    'background-color': 'green',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('BUY'),
                        'column_id': 'STATUS'
                        },
                    'background-color': 'green',
                },
                {
                    'if': {
                        'column_id': 'Price'
                        },
                    'text-align': 'right',
                },
                                {
                    'if': {
                        'column_id': 'RSI'
                        },
                    'text-align': 'right',
                }
            ])]

def render_wl2_table(df):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    render_conditional = '({RSI} >='+str(RSI_TO_BUY)+' && {RSI}<='+str(T_BUY)+') || ({RSI}>='+str(T_SELL)+' && {RSI}<='+str(RSI_TO_SELL)+')'
    return [
            dash_table.DataTable(data=df.to_dict('records'), 
            columns=[{"name": i, "id": i,'type':'numeric', 'format':Format(precision=2,scheme=Scheme.fixed)} if i =='RSI' or i=='Price' else 
            {"name": i, "id": i}for i in df.columns],
            id='watchlist2_Table',
            page_size=25,
            style_header={'textAlign': 'center',
                        'color':'white',
                        'background-color':'#02457a',
                        'font-size':'16px'},
            style_cell={'textAlign': 'left',
                        'color':'black',
                        'font-size':'13px'},
            style_data_conditional=[
                {
                    'if': {
                        'filter_query':render_conditional,
                        'column_id': 'RSI'
                        },
                    'background-color': 'yellow',
                },
                {
                    'if': {
                        'filter_query':render_conditional,
                        'column_id': 'STATUS'
                        },
                    'background-color': 'yellow',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('SELL'),
                        'column_id': 'RSI'
                        },
                    'background-color': 'red',                 
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('SELL'),
                        'column_id': 'STATUS'
                        },
                    'background-color': 'red',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('BUY'),
                        'column_id': 'RSI'
                        },
                    'background-color': 'green',
                },
                {
                    'if': {
                        'filter_query':'{{STATUS}} = {}'.format('BUY'),
                        'column_id': 'STATUS'
                        },
                    'background-color': 'green',
                },
                {
                    'if': {
                        'column_id': 'Price'
                        },
                    'text-align': 'right',
                },
                                {
                    'if': {
                        'column_id': 'RSI'
                        },
                    'text-align': 'right',
                }
            ])]

def render_dropdown_menu(options, menuId, defaultVal):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    return dbc.Row([dcc.Dropdown(
                            id=menuId,
                            options=[                             
                                {"label": stock, "value": stock}
                                for stock in options
                            ],
                            value=defaultVal,
                            clearable=False,
                            className="dropdown",
                            ),
                    ]
            )

def render_options_checklist(id_opts):
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    return html.Div(
    [
        dbc.Checklist(
            options=[
                {"label": "SELL", "value": 1},
                {"label": "BUY", "value": 2},
                {"label": "HOLD", "value": 3},
            ],
            value=[1,2,3],
            id= id_opts,
            inline=True,
            switch=True,
        ),
    ]
)

def main_dashboard_header():
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    return [   dbc.Col([
                    html.Div(id='fakeOutput'),
                    html.Div(id='fakeOutputAdjust'),
                    html.Div(id='fakeOutputTest'),
                    html.Div(id='fakeOutputRemove'),
                    html.Div
                    (html.H1(
                        id='title_T',
                        children="RSI - AA",
                        className='text-center', 
                        style={
                            'color':'white'}), 
                        style={
                            'border':'1px solid',
                            'border-radius':'20px',
                            'background-color':
                            '#001B48'}),
                    dbc.Row([
                    dbc.Col(dbc.Button("ADJUST", id='adjust-data-button',style={'background-color':'#001B48', 'border':'1px solid #001B48'}, className="ms-auto", n_clicks=0)),
                    dbc.Col(dbc.Button("UPDATE", id='update-data-button',style={'background-color':'#001B48', 'border':'1px solid #001B48'}, className="ms-auto", n_clicks=0)),
                    dbc.Col(dbc.Button("ADD", id='add-new-stock',style={'background-color':'#001B48', 'border':'1px solid #001B48'}, className="ms-auto", n_clicks=0)),
                    dbc.Col(dbc.Button("REMOVE", id='remove-stock',style={'background-color':'#001B48', 'border':'1px solid #001B48'}, className="ms-auto", n_clicks=0))
 
                    ],                    style={
                            'padding':'2%'
                    })
                ]),
                dbc.Col(
                    html.Div(children=[
                    dbc.Row([
                    dbc.Col(html.Div(children="Company")),
                    dbc.Col(render_dropdown_menu(companies, "company-filter", "AA")),
                    dbc.Col(render_options_checklist("options-checkbox"))
                    ])
                    ]))
            ]

def watchlist1_dashboard():
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    return [   dbc.Col([
                    html.Div(id='wl1fakeOutput'),
                    html.Div(id='wl1fakeOutputTest'),
                    html.Div(id='wl1fakeOutputRemove'),
                    html.Div
                    (html.H1(
                        id='wl1_title_T',
                        children="WL1",
                        className='text-center', 
                        style={
                            'color':'white'}), 
                        style={
                            'border':'1px solid',
                            'border-radius':'20px',
                            'background-color':
                            '#001B48'})]),
                dbc.Col(
                    html.Div(children=[
                    dbc.Row([
                    dbc.Col(html.Div(children="Company")),
                    dbc.Col(render_dropdown_menu(['WATCHLIST']+companies, "wl1_company-filter", "WATCHLIST"))
                    ])
                    ]))
            ]

def watchlist2_dashboard():
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    return [   dbc.Col([
                    html.Div(id='wl2fakeOutput'),
                    html.Div(id='wl2fakeOutputTest'),
                    html.Div(id='wl2fakeOutputRemove'),
                    html.Div
                    (html.H1(
                        id='wl2_title_T',
                        children="WL2",
                        className='text-center', 
                        style={
                            'color':'white'}), 
                        style={
                            'border':'1px solid',
                            'border-radius':'20px',
                            'background-color':
                            '#001B48'})]),
                dbc.Col(
                    html.Div(children=[
                    dbc.Row([
                    dbc.Col(html.Div(children="Company")),
                    dbc.Col(render_dropdown_menu(['WATCHLIST2']+companies, "wl2_company-filter","WATCHLIST2"))
                    ])
                    ]))
            ]        

def main():
    global RSI_TO_SELL, RSI_TO_BUY, T_BUY, T_SELL
    print("BUY AND TBUY", RSI_TO_BUY, T_BUY, type(RSI_TO_BUY),type(T_BUY))
    print("SELL AND TSELL", RSI_TO_SELL,T_SELL, type(RSI_TO_SELL),type(T_SELL))
    webbrowser.open("http://127.0.0.1:8050/")
    source=pathlib.Path(__file__).parent.resolve()
    df=pd.read_csv('{0}/data_base/ALL.csv'.format(source))
    df = filter_by_options(df,[True,True,True])
    app.layout=html.Div([
        dbc.Container([dbc.Spinner(children=[dbc.Container([
            html.Div(id='shutdown'),
            dbc.Row([
                dbc.NavbarSimple([
                    dbc.NavLink("Main Dashboard", id='mdpage',href="/maindashboard", style={'color':'white'}),
                    dbc.NavLink("Watch List 1",id='wl1page', href="/wl1", style={'color':'white'}),
                    dbc.NavLink("Watch List 2",id='wl2page', href="/wl2", style={'color':'white'})
                ],
                color='#001B48')
            ]),
            dbc.Row(main_dashboard_header(),
            id='dashboard-header', 
            style={
                        'padding':'2.5%'
                    }),
            dbc.Row(render_table(df),
            id='dashboard-content'),
            dbc.Row([
                render_modal_update(),
                render_modal_adjust(),
                render_modal_add(),
                render_modal_remove()
            ])
            
        ]
    )],size='md', color='primary',fullscreen=True, id="Spinner-upload")])])
    if __name__ == "__main__":
        app.run_server(debug=False)

main()