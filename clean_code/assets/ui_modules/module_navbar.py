import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

def build_navbar(img_path,symbol,navbrand_id):
    navbar=dbc.Navbar(
        dbc.Container([
                dbc.Row(
                    dbc.Col
                    ([
                        html.Img(src=img_path, height='30px'),
                        dbc.NavbarBrand(symbol, class_name="ms-2",id=navbrand_id)
                    ])
                )
        ]), color="#2a3338")
    return navbar