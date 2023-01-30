import dash_bootstrap_components as dbc
from dash import html

def build_action_button(action, color, ss):
    return (
        dbc.Button(action, color=color, className=ss)
    )