import dash
from dash import dcc
from dash import html


def build_dropdown(label_value_array, dropdown_id):
    options_dropdown=[{'label':f'{element}', 'value':f'{element}'} for element in label_value_array]
    dropdown= dcc.Dropdown(
            id=dropdown_id,
            options=options_dropdown
        )
    return dropdown