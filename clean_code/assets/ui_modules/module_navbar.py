import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

def build_navbar(img_path,symbol,navbrand_id):
    navbar=dbc.Navbar(
        dbc.Container([
                dbc.Row(html.A([
                        #html.Img(src=img_path, height='80px'),
                       dbc.Col([dbc.NavbarBrand(symbol, class_name="ms-2",id=navbrand_id,style={'color':'white', 'font-size':'40px'}),
                       dbc.NavbarBrand("Dashboard Admin",id="admin_label",style={'color':'white', 'font-size':'40px', 'text-align':'right'})])
                    ])
                )])
        , color="#2a3338")
    return navbar