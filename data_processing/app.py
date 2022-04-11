# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html
import plotly.express as px
from c_impedance import c_impedance_plot
from mudbat_plot import mudbat_plot
import pandas as pd

app = Dash(__name__)

app.layout = html.Main(children=[
    html.Div(children=[
        html.H1(children=['DirtViz']),
        html.H3(children=['A soil-battery data dashboard made with Dash'])
    ]),
    html.Div(className="flex", children=[
        html.Div(className="flexItem", children= [dcc.Graph(figure=c_impedance_plot())]),
        html.Div(className="flexItem", children= [dcc.Graph(figure=mudbat_plot())]),
        html.Div(id="graph3",className="flexItem"),
        html.Div(id="graph4",className="flexItem"),
        html.Div(id="graph5",className="flexItem"),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
