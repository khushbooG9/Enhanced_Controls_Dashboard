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

def build_top_panel():
    """
    Function to build top panel for 2 graph placeholders
    TBD
    """

    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            html.Div(
                id="left-graph",
                children = [
                    build_left_graph(),
                ]
            ),
            html.Div(
                id="right-graph",
                children= [
                    build_right_graph(),
                ]
            ),
        ],
    )

def left_graph():
    #df, estimation, name = get_data(settings_dict, state_dict)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

    fig.append_trace(go.Scatter(

        x = [i for i in range(10)],
        y = [i for i in range(10)],
        name= "placeholder",
        ), row=1, col=1)

    fig.append_trace(go.Scatter(
        x= [i for i in range(10)],
        y= [i for i in range(10)],
        name = "placeholder",
        ), row=2, col=1)
    fig.update_yaxes(title_text="Placeholder 1", row=1, col=1,showline=True, linewidth=2, linecolor='#e67300', mirror=True)
    fig.update_yaxes(title_text="Placeholder 1", row=2, col=1,showline=True, linewidth=2, linecolor='#e67300', mirror=True, title_standoff=2)
    fig.update_xaxes(row=1, col=1,showline=True, linewidth=2, linecolor='#e67300', mirror=True)
    fig.update_layout(width=500, height=350,paper_bgcolor = "#EFEDED",legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.05,
    xanchor="right",
    x=1), 
	)
    return fig

def build_left_graph():
    """
    function to build left graph
    Reference: https://plotly.com/python/subplots/
    """

    return dcc.Graph(
        id = "left-graph-fig", figure = left_graph(),
    )

def right_graph():
    #df, estimation, name = get_data(settings_dict, state_dict)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[i for i in range(10)],
        y=[i for i in range(10)],
		name = "placeholder right graph",
	)
	)
    fig.update_xaxes(showline=True, linewidth=2, linecolor='#e67300', mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='#e67300', mirror=True)
    fig.update_layout(paper_bgcolor = "#EFEDED", width=500, height=350,legend = dict(
     orientation="h",
	 yanchor="bottom",
	 y=1.05,
	 xanchor="right",
	 x=1,
	 ),
	xaxis_title="x-axis",
	yaxis_title="y-axis",
	
        )


    return fig

def build_right_graph():
    """
    Function to build right graph
    Reference: https://plotly.com/python/line-charts/
    """


    return dcc.Graph(
        id="right-graph-fig", figure = right_graph(),
    )

def revenue_block():
	return html.Div(
        id="revenue-block",
        children = [
            html.H6("Revenue"),
            html.Br(),
            html.Div(
                id="revenue-label",
                children = [
                    html.Label("Day Ahead Estimate"),
                    dcc.Input(id="revenue1", type='text'),
                ]
            ),

            html.Br(),
            html.Div(
                id="revenue-label",
                children = [
                    html.Label("Actual, Not Adjusted"),
                    dcc.Input(id="revenue2", type='text'),
                ]
            ),

            html.Br(),
            html.Div(
                id="revenue-label",
                children = [
                    html.Label("Actual, Real Time Adjusted"),
                    dcc.Input(id="revenue3", type='text'),
                ]
            ),

        ]
    )


def build_bottom_panel():
    """
    Function to build top panel for 2 graph placeholders
    TBD
    """
    return html.Div(
        id="bottom-section-container",
        className="row",
        children=[
            html.Div(
                #id="left-graph",

            ),
            html.Div(
                id="bottom-panel-container",
                children= [
                    revenue_block(),
                ]
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
                children = [build_top_panel(), build_bottom_panel()],
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