import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import datetime

import yfinance as yf
import pandas as pd


import assets.utils.data_handler as dh

from assets.ui_modules.module_navbar import build_navbar as navbar
from assets.ui_modules.module_dropdown import build_dropdown as dropdown_menu
from assets.ui_modules.module_table import build_table as table


yf.pdr_override()
pd.options.display.float_format = '{:,.2f}'.format

symbols=dh.get_symbols()

app=dash.Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.JOURNAL],
    meta_tags=[{'name':'viewport',
    'content':'width=divice-width, initial-scale=1.0'
    }])

"""UPDATES SELECTED SYMBOL"""
@app.callback(
    [Output("rsi_cointainer","children"),Output("current_symbol","children")],
    Input("symbols_dropdown", "value"),
    State("symbols_dropdown", "value")
)
def update_selected_symbol(symbol, state):
    if state:
        start=datetime.datetime(2016,1,1)
        end=datetime.date.today() 
        return [table(dh.get_dataframe(symbol),dh.get_table_conditional(),"rsi_table"),symbol]
    else:
        return [table(pd.DataFrame(),'True',"rsi_table"), "Main"]


def main():
    app.layout= html.Div([
        navbar(app.get_asset_url("images/aa.png"),"MAIN","current_symbol"),
        dropdown_menu(symbols, 'symbols_dropdown'),
        dbc.Row(table(pd.DataFrame(),'True',"rsi_table"), id="rsi_cointainer", style={"width":"45%","heigth":"45%"})
    ])
    if __name__ == "__main__":
        app.run_server(debug=True)

main()
