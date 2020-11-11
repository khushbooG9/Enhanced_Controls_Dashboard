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

def build_settings_tab():
    """
    Function to put together the settings tab
    """
    return [
    #system_configuration_panel(),
        html.Div(
            id="system-configuration-menu",
            children = html.H2("No settings yet"),
        )]

def build_buttons_panel():
    """
    Function to generate a panel for buttons on left side
    """
    return html.Div(
      id="buttons-panel",
      className="row",
      children=[
          html.Div(
              id="card-1",
              children=[
                  html.Button( className="", id="button1",children="Arbitrage",n_clicks=0),
                  html.Button( className="", id="button1", children="Peak Shaving", n_clicks=0),
                  html.Button( className="", id="button1", children="Demand Shaping", n_clicks=0),
                  html.Button( className="", id="button1", children="System Capacity", n_clicks=0),
                  html.Button( className="", id="button1", children="Frequency Regulation", n_clicks=0),
                  html.Button( className="", id="button1", children="Spinning/Non-Spinning Reserve", n_clicks=0),
                  html.Button( className="", id="button1", children="Volt/Var", n_clicks=0),
                  html.Button( className="", id="button1", children="Co-optimize", n_clicks=0),
              ],
          ),
          html.Div(
              id="card-2",
              children=[
                  html.Button("Data Input", className="", id="button2"),
                 
              ],
          ),
          
      ],

    )

def build_simulation_tab():
    """
    Function to put together the simulation  tab
    """
    return  ( html.Div(
        id="simulation-container",
        children = [
            build_buttons_panel(),
            html.Div(
                id="graphs-container",
                children = html.H2("Working on it"),
            ),
        ],
    ),
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
                        label="Control Dashboard",
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
                html.Div(id="app-content"),
                
            ],
        ),

    ],
  )

app.layout = serve_layout

@app.callback(
    output = [Output("app-content", "children")],
    inputs =        [Input("app-tabs","value")],
    #state = [State("value-setter-store","data"), State("dropdown-store", "data")]
    )
def render_tab_contents(tab_switch):
    """
    """
    if tab_switch=="tab2":
        
        return build_simulation_tab()

    return build_settings_tab()

if __name__ == '__main__':
    app.run_server(debug=True)