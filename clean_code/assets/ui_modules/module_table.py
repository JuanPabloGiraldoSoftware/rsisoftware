from dash import dash_table
from dash.dash_table.Format import Format, Scheme, Trim

def build_table(dataframe, render_conditional, table_id):

    table = [dash_table.DataTable(data=dataframe.to_dict('records'), 
            columns=[{"name": i, "id": i,'type':'numeric', 'format':Format(precision=2,scheme=Scheme.fixed)} if i =='RSI' or i=='Price' else 
            {"name": i, "id": i}for i in dataframe.columns],
            id=table_id,
            page_size=25,
            style_as_list_view=True,
            style_header={'textAlign': 'center',
                        'border-radius': '3px',
                        'color': 'white',
                        'background-color':'#2a3338',
                        'margin': '0 auto',
                        'font-size': '16px'},
            style_cell={'textAlign': 'center',
                        'border-radius': '3px',
                        'color': 'white',
                        'background-color':'gray',
                        'margin': '0 auto',
                        'font-size': '12px'},
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

    return table