from app import *
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from  plotly.subplots import make_subplots 
import plotly.graph_objects as go
import dash_daq as daq
import dash_table
import pandas as pd 

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Energy Storage Control"),
                    html.H6("Enhanced Control Dashboard"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Img(id="logo", src=app.get_asset_url("pnnl_logo.png")),
                ],
            ),
        ],
    )

def build_tabs():
    """
    Function to build both the tabs
    """
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Settings",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Simulation Dashboard",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),

                ],
            )
        ],
    )


def serve_layout():
    return html.Div(
    id="big-app-container",
    children = [
    build_banner(),
    html.Div(
            id="app-container",
            children=[
                build_tabs(),
                html.H6("Starter")
            ],
        ),

    ],
  )

app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(debug=True)