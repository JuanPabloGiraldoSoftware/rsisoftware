import plotly.express as px
from dash import dcc
import pandas as pd

def build_linebar(df,x,y,title,id):
    if x=="": return dcc.Graph(id=id)
    fig=px.line(df, x=x, y=y, title=title)
    linebar=dcc.Graph(figure=fig,id=id)
    return linebar