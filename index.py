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
from BatteryClass import * 

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

def data_upload_panel():

    return  html.Div(
    id = "configuration-select-menu-wrapper",
    children = [
    html.Div(
        id="configuration-select-menu",
        children = [
                html.H6("Upload Data"),
                html.Br(),
                html.Br(),


                html.Div(
                    id = "dropdown-label",
                    children = [
                        html.Div(
                            children = [
                            html.Label("Load Profile Data"),
                            dcc.DatePickerRange(
                                start_date_placeholder_text="Start Period",
                                end_date_placeholder_text="End Period",
                                
                            ) 
                            ]
                        ),
                        html.Div(
                            children =[
                            dcc.Upload(
                            id="upload-load-profile-data",
                            children = html.Div([
                           'Drag and Drop or ',
                            html.A('Select a File')
                            ]) 
                            ),
                            ]
                        ),
                        html.Hr(),
                        #html.Div(id='output-upload-cable-data'),
                    ]
                ),
                html.Div(id='output-upload-load-profile-data'),
                html.Br(),
                html.Div(
                    id = "dropdown-label",
                    children = [
                        html.Div(
                            children = [
                            html.Label("Energy Price Data"),
                            dcc.DatePickerRange(
                                start_date_placeholder_text="Start Period",
                                end_date_placeholder_text="End Period",
                                
                            ) 
                            ]
                        ),
                        html.Div(
                            children = [
                            dcc.Upload(
                            id="upload-energy-price-data",
                            children = html.Div([
                           'Drag and Drop or ',
                            html.A('Select a File')
                            ]) 
                            ),
                            ]
                        ),
                        html.Hr(),
                        #html.Div(id='output-upload-cable-data'),
                    ]
                ),
                html.Div(id='output-upload-energy-price-data'),
                html.Br(),
                html.Div(
                    id = "dropdown-label",
                    children = [
                        html.Div(
                            children = [
                            html.Label("ESS Data"),
                            ]
                        ),
                        html.Div(
                            children = [
                            dcc.Upload(
                            id="upload-ess-data",
                            children = html.Div([
                           'Drag and Drop or ',
                            html.A('Select a File')
                            ]) 
                            ),
                            ]
                        ),
                        html.Hr(),
                        #html.Div(id='output-upload-cable-data'),
                    ]
                ),
                html.Div(id='output-upload-ess-data'),

                ]
    ),
    html.Br(),
]

)

def build_usecase_line(line_num, label, switch_value, dd_value,value):
    return html.Div(
        id=line_num,
        className="usecase-line-row",
        children=[
            html.Label(label, className="usecase-label"),
            daq.BooleanSwitch(on=False, className="usecase-switch", color="#cc3300", id=switch_value),
            dcc.Dropdown(
                className = "usecase-dropdown",
                id = dd_value,
                options = [
                    {'label':'1', 'value':1},
                    {'label':'2', 'value':2},
                    {'label':'3', 'value':3},
                    {'label':'4', 'value':4}
                ],
                disabled=True,
            ),
            html.Button("Configure", className="usecase-set-button",id=value, disabled=True, n_clicks=0)        
        ],

    )

def usecase_dcr_popup():
    """
    Function to get the life mode pop-up
    """
    return html.Div(
        id="markdown",
        style = {"display":"none"},
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown-close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        id="markdown-content",
                        className="markdown-content",
                        children = [
                        html.Div(
                            id = "markdown-panel",
                            children = [ html.Div (
                                id = "markdown-panel2",
                                children = [
                                html.H6("Configuration"),
                                html.Br(),
                                html.Br(),
                                html.Div(
                                        id="usecase-dcr-header",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Setting Name", className="usecase-dcr-label"),
                                            html.Label("Setting Input", className="usecase-setting-input")
                                        ],

                                    ),
                                html.Br(),
                                html.Div(
                                        id="peak-charge",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Peak Charge", className="usecase-dcr-label"),
                                            daq.NumericInput(id="peak-charge-input", className="usecase-setting-input", size=200, min=0, max=1000, value=5)
                                        ],

                                    ),
                                html.Br(),
                                html.Div(
                                        id="threshold",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Threshold", className="usecase-dcr-label"),
                                            daq.NumericInput(id="threshold-input", className="usecase-setting-input", size=200, min=0, max=1000, value=5)
                                        ],

                                    ),
                                html.Br(),
                                html.Div(
                                        id="uncertainity-budget",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Uncertainity Budget", className="usecase-dcr-label"),
                                            daq.NumericInput(id="uncertainity-budget-input", className="usecase-setting-input", size=200, min=0, max=1000, value=5)
                                        ],

                                    ),
                                html.Br(),
                                html.Div(
                                        id="control-type",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Control Type", className="usecase-dcr-label"),
                                            daq.BooleanSwitch(on=False,id="control-type-input1" ,className="usecase-switch", color="#cc3300", label="Optimization"),
                                            daq.BooleanSwitch(on=False,id="control-type-input2" ,className="usecase-switch", color="#cc3300", label="Rule-based"),
                                            
                                        ],

                                    ),
                                ]
                                
                            ),

                            html.Button("Update", className="", id="usecase-dcr-set-btn", n_clicks=0),

                             ],

                            ),
                        ]
                    ),

                ]
            )
        )

    )

def usecase_pfc_popup():
    """
    Function to get the life mode pop-up
    """
    return html.Div(
        id="markdown2",
        style = {"display":"none"},
        className="modal",
        children=(
            html.Div(
                id="markdown-container2",
                className="markdown-container2",
                children=[
                    html.Div(
                        className="close-container2",
                        children=html.Button(
                            "Close",
                            id="markdown-close2",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        id="markdown-content2",
                        className="markdown-conten2t",
                        children = [
                        
                        html.Div(
                            id = "markdown-panel2a",
                            children = [ html.Div (
                                id = "markdown-panel2b",
                                      children = [
                                html.H6("Configuration"),
                                html.Br(),
                                html.Br(),
                                html.Div(
                                        id="usecase-pfc-header",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Setting Name", className="usecase-pfc-label"),
                                            html.Label("Setting Input", className="usecase-setting-input")
                                        ],

                                    ),
                                html.Br(),
                                html.Div(
                                        id="load-power-factor",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Load Power Factor", className="usecase-pfc-label-label"),
                                            daq.NumericInput(id="load-power-factor-input", className="usecase-setting-input", size=200, min=0, max=1000, value=5)
                                        ],

                                    ),
                                html.Br(),
                                html.Div(
                                        id="power-factor-limit",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Power Factor Limit", className="usecase-dcr-label"),
                                            daq.NumericInput(id="power-factor-limit-input", className="usecase-setting-input", size=200, min=0, max=1000, value=5)
                                        ],

                                    ),
                                html.Br(),
                                html.Div(
                                        id="control-type2",
                                        className="usecase-line-row",
                                        children=[
                                            html.Label("Control Type", className="usecase-dcr-label"),
                                            daq.BooleanSwitch(on=False,id="control-type-input21" ,className="usecase-switch", color="#cc3300", label="Optimization"),
                                            daq.BooleanSwitch(on=False,id="control-type-input22" ,className="usecase-switch", color="#cc3300", label="Rule-based"),
                                            
                                        ],

                                    ),
                                ]
                                
                            ),

                            html.Button("Update", className="", id="usecase-pfc-set-btn", n_clicks=0),

                             ],

                            ),
                        ]
                    ),

                ]
            )
        )

    )

def configuration_panel():
    """
    Function to get the system configuration panel
    """
    return  html.Div(
    id = "configuration-select-menu-wrapper",
    children = [
    html.Div(
        id = "configuration-select-menu",
        children = [
        html.H6("Usecase Configuration"),
        html.Br(),
        html.Br(),
        html.Div(
            id="usecase-header",
            className="usecase-line-row",
            children=[
                html.Label("Usecase", className="usecase-label"),
                html.Label("Select", className="usecase-switch"),
                html.Label("Priority", className="usecase-dropdown"),
                "Configure Usecase",#html.Div(col, className="value-setter")
            ],
        ),
        build_usecase_line("demand-charge-reduction", "Demand Charge Reduction","switch_dcr" ,"dd_dcr","dcr"),
        html.Br(),
        build_usecase_line("power-factor-correction","Power Factor Correction","switch_pfc","dd_pfc","pfc"),
        html.Br(),
        build_usecase_line("arbitrage", "Arbitrage","switch_arb","dd_arb", "arb"),
        html.Br(),
        build_usecase_line("revserves-placement", "Reserves Placement","switch_rp","dd_rp", "rp"),
        ]
    ),
    html.Br(),
    html.Br(),
    html.Div(
        id = "dropdown-button",
        children = [html.Button("Update", className="",  n_clicks=0),]
        ),
]

)

def build_settings_tab():
    """
    Function to put together the settings tab
    """
    return [
    #system_configuration_panel(),
        html.Div(
            id="system-configuration-menu",
            children = [configuration_panel(), data_upload_panel()],
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
    battery_obj = BatteryClass('dict.json')  # make object
    battery_obj.get_data()
    
    battery_obj.set_load_forecast()
    battery_obj.DA_optimal_quantities()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

    fig.append_trace(go.Scatter(

        x = [i for i in range(len(battery_obj.grid_react_power_prediction))],
        y = battery_obj.grid_react_power_prediction,
        name= "Total Reactive Power Grid ",
        ), row=1, col=1)
    fig.add_trace(go.Scatter(

        x = [i for i in range(len(battery_obj.grid_react_power_prediction))],
        y = battery_obj.battery_react_power_prediction,
        name= "Reactive Power Battery",
        ), row=1, col=1)
    fig.add_trace(go.Scatter(

        x = [i for i in range(len(battery_obj.grid_react_power_prediction))],
        y = battery_obj.load_up*battery_obj.load_pf,
        name= "Predicted Reactive Power Load",
        ), row=1, col=1)

    fig.append_trace(go.Scatter(
        x= [i for i in range(len(battery_obj.grid_react_power_prediction))],
        y= battery_obj.grid_power_factor,
        name = "New Power Factor",
        ), row=2, col=1)

    fig.add_trace(go.Scatter(

        x = [i for i in range(len(battery_obj.grid_react_power_prediction))],
        y = battery_obj.grid_original_power_factor,
        name= "Old Power Factor", line = dict(dash="dash")
        ), row=2, col=1)


    fig.update_yaxes(title_text="kVar", row=1, col=1,showline=True, linewidth=2, linecolor='#e67300', mirror=True)
    fig.update_yaxes(title_text="cosphi", row=2, col=1,showline=True, linewidth=2, linecolor='#e67300', mirror=True, title_standoff=2)
    fig.update_xaxes(row=1, col=1,showline=True, linewidth=2, linecolor='#e67300', mirror=True)
    fig.update_xaxes(title_text="Hours", row=2, col=1,showline=True, linewidth=2, linecolor="#e67300", mirror=True)
    fig.update_layout(title= "Grid Side Results" ,width=500, height=350,paper_bgcolor = "#EFEDED",legend=dict(
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
    battery_obj = BatteryClass('dict.json')  # make object
    battery_obj.get_data()
    
    battery_obj.set_load_forecast()
    battery_obj.DA_optimal_quantities()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[i for i in range(len(battery_obj.battery_setpoints))],
        y=[i for i in battery_obj.battery_setpoints],
		name = 'Battery Power (Charge/Discharge)',
	)
	)
    fig.add_trace(go.Scatter(
        x=[i for i in range(len(battery_obj.battery_setpoints))],
        y=[battery_obj.peak_load_prediction]*battery_obj.windowLength,
        name = 'Peak Load',
    )
    )
    fig.add_trace(go.Scatter(
        x=[i for i in range(len(battery_obj.battery_setpoints))],
        y=[i for i in battery_obj.grid_load_prediction],
        name = 'Grid Load',
    )
    )
    fig.add_trace(go.Scatter(
        x=[i for i in range(len(battery_obj.battery_setpoints))],
        y=[i for i in battery_obj.load_predict],
        name = 'Load Prediction',
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
	xaxis_title="Hours",
	yaxis_title="kW",
	
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
                usecase_dcr_popup(),
                usecase_pfc_popup(),
                
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

@app.callback(
    Output("markdown", "style"),
    [Input("dcr", "n_clicks"), Input("markdown-close", "n_clicks")],
)
def update_click_output1(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        #print(prop_id)
        if prop_id == "dcr" and button_click!=0:
            return {"display": "block"}

    return {"display": "none"}

@app.callback(
    Output("markdown2", "style"),
    [Input("pfc", "n_clicks"), Input("markdown-close2", "n_clicks")],
)
def update_click_output1(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        #print(prop_id)
        if prop_id == "pfc" and button_click!=0:
            return {"display": "block"}

    return {"display": "none"}

@app.callback(
	output = [Output("dd_dcr","disabled"), Output("dd_pfc","disabled"), Output("dd_arb", "disabled"), Output("dd_rp", "disabled"), \
	Output("dcr","disabled"), Output("pfc", "disabled"), Output("arb","disabled"), Output("rp","disabled")],
	inputs = [Input("switch_dcr","on"), Input("switch_pfc", "on"), Output("switch_arb","on"), Output("switch_rp","on")],
)
def make_usecase_active(s1,s2,s3,s4):
	print(s1)
	if s1==True:
		d1a, d1b = False, False
	else:
		d1a, d1b = True, True
	if s2==True:
		d2a, d2b = False, False
	else:
		d2a, d2b = True, True
	if s3==True:
		d3a, d3b = False, False
	else:
		d3a, d3b = True, True
	if s4==True:
		d4a, d4b = False, False
	else:
		d4a, d4b = True, True
	return [d1a, d2a, d3a, d4a, d1b, d2b, d3b, d4b]


if __name__ == '__main__':
    app.run_server(debug=True)