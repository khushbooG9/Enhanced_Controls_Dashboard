from app import *
import dash
import base64
import io
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_daq as daq
import dash_table
import pandas as pd
from battery_class_new import *
from sim_runner_no_dashboard import *
# from BatteryClass import *
from collections import deque
import random
import json
import jsonpickle
from json import JSONEncoder


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


def init_usecase():

    with open("dict.json", 'r', encoding='utf-8') as lp:
        gen_config = json.load(lp)

    with open("control_fields.json", 'r', encoding='utf-8') as lp:
        control_config = json.load(lp)

    use_case_library = construct_use_case_library(gen_config, control_config)

    return use_case_library


def init_gen_config():
    with open("dict.json", 'r', encoding='utf-8') as lp:
        gen_config = json.load(lp)
    return gen_config


def init_control_config():
    with open("control_fields.json", 'r', encoding='utf-8') as lp:
        control_config = json.load(lp)
    return control_config


def init_data_config():
    with open("data_paths.json", 'r', encoding='utf-8') as lp:
        data_config = json.load(lp)
    return data_config


def data_upload_panel():
    return html.Div(
        id="configuration-select-menu-wrapper",
        children=[
            html.Div(
                id="configuration-select-menu",
                children=[
                    html.H6("Upload"),
                    html.Br(),
                    #html.Br(),
                    html.Div(
                        id="dropdown-label",
                        children=[
                            html.Div(
                                children=[
                                    html.Label("Load Profile Data"),
                                    dcc.DatePickerRange(
                                        start_date_placeholder_text="Start Period",
                                        end_date_placeholder_text="End Period",
                                        calendar_orientation='horizontal',

                                    )
                                ]
                            ),
                            html.Div(
                                children=[
                                    html.Label("Upload Profile Data"),
                                    dcc.Upload(
                                        id="upload-load-profile-data",
                                        children=html.Div(
                                            ["Drag and drop or select a file"]),
                                        style={
                                            'width': '200%',
                                            'height': '30px',
                                            'lineHeight': '30px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '2px',
                                            'textAlign': 'center',
                                            'margin': '10px',
                                            'fontSize': '12px'
                                        }
                                    ),
                                ]
                            ),
                            html.Hr(),
                            # html.Div(id='output-upload-cable-data'),
                        ]
                    ),
                    html.Br(),
                    html.Div(id='output-upload-load-profile-data'),
                    html.Br(),
                    html.Div(
                        id="dropdown-label",
                        children=[
                            html.Div(
                                children=[
                                    html.Label("Energy Price Data"),
                                    dcc.DatePickerRange(
                                        start_date_placeholder_text="Start Period",
                                        end_date_placeholder_text="End Period",

                                    )
                                ]
                            ),
                            html.Div(
                                children=[
                                    html.Label("Upload Energy Price Data"),
                                    dcc.Upload(
                                        id="upload-energy-price-data",
                                        children=html.Div(["Drag and drop or click to select a file to upload." ]),
                                        style={
                                            'width': '200%',
                                            'height': '30px',
                                            'lineHeight': '30px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '2px',
                                            'textAlign': 'center',
                                            'margin': '10px',
                                            'fontSize': '12px'
                                        }
                                    ),
                                ]
                            ),
                            html.Hr(),
                            # html.Div(id='output-upload-cable-data'),
                        ]
                    ),
                    html.Br(),
                    html.Div(id='output-upload-energy-price-data'),
                    html.Br(),
                    html.Div(
                        id="dropdown-label",
                        children=[
                            html.Div(
                                children=[
                                    html.Label("ESS Data"),
                                ]
                            ),
                            html.Div(
                                children=[
                                    dcc.Upload(
                                        id="upload-ess-data",
                                        children=html.Div(["Drag and drop or click to select a file to upload."
                                        ]),
                                        style={
                                            'width': '200%',
                                            'height': '30px',
                                            'lineHeight': '30px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '2px',
                                            'textAlign': 'center',
                                            'margin': '10px',
                                            'fontSize': '12px'
                                        }
                                    ),
                                ]
                            ),
                            html.Hr(),
                            # html.Div(id='output-upload-cable-data'),
                        ]
                    ),
                    html.Div(id='output-upload-ess-data'),

                ]
            ),
            html.Br(),
        ]

    )

# @app.callback(Output('data', 'contents'),
#             [Input('upload-energy-price-data', 'contents')])
# def update_upload_data(price_data):
#     content_type, content_string = price_data.split(',')
#     decoded = base64.b64decode(content_string)
#     df = pd.read_csv(
#         io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
#     return df


def build_usecase_line(line_num, label, switch_value, dd_value, value):
    return html.Div(
        id=line_num,
        className="usecase-line-row",
        children=[
            html.Label(label, className="usecase-label"),
            daq.BooleanSwitch(on=False, className="usecase-switch", color="#cc3300", id=switch_value),
            dcc.Dropdown(
                className="usecase-dropdown",
                id=dd_value,
                options=[
                    {'label': '1', 'value': 1},
                    {'label': '2', 'value': 2},
                    {'label': '3', 'value': 3},
                    {'label': '4', 'value': 4}
                ],
                disabled=True,
            ),
            html.Button("Configure", className="usecase-set-button", id=value, disabled=True, n_clicks=0)
        ],

    )


def usecase_dcr_popup():
    """
    Function to get the life mode pop-up
    """
    return html.Div(
        id="markdown",
        style={"display": "none"},
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
                        children=[
                            html.Div(
                                id="markdown-panela",
                                children=[html.Div(
                                    id="markdown-panelb",
                                    children=[
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
                                                daq.NumericInput(id="peak-charge-input",
                                                                 className="usecase-setting-input", size=200, min=0,
                                                                 max=1000, value=5)
                                            ],

                                        ),
                                        html.Br(),
                                        html.Div(
                                            id="threshold",
                                            className="usecase-line-row",
                                            children=[
                                                html.Label("Threshold", className="usecase-dcr-label"),
                                                daq.NumericInput(id="threshold-input",
                                                                 className="usecase-setting-input", size=200, min=0,
                                                                 max=1000, value=5)
                                            ],

                                        ),
                                        html.Br(),
                                        html.Div(
                                            id="uncertainity-budget",
                                            className="usecase-line-row",
                                            children=[
                                                html.Label("Uncertainity Budget", className="usecase-dcr-label"),
                                                daq.NumericInput(id="uncertainity-budget-input",
                                                                 className="usecase-setting-input", size=200, min=0,
                                                                 max=1000, value=5)
                                            ],

                                        ),
                                        html.Br(),
                                        html.Div(
                                            id="control-type",
                                            className="usecase-line-row",
                                            children=[
                                                html.Label("Control Type", className="usecase-dcr-label"),
                                                daq.BooleanSwitch(on=False, id="control-type-input1",
                                                                  className="usecase-switch", color="#cc3300",
                                                                  label="Optimization"),
                                                daq.BooleanSwitch(on=False, id="control-type-input2",
                                                                  className="usecase-switch", color="#cc3300",
                                                                  label="Rule-based"),

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
        style={"display": "none"},
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
                        className="markdown-content2",
                        children=[

                            html.Div(
                                id="markdown-panel2a",
                                children=[html.Div(
                                    id="markdown-panel2b",
                                    children=[
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
                                                html.Label("Load Power Factor", className="usecase-pfc-label"),
                                                daq.NumericInput(id="load-power-factor-input",
                                                                 className="usecase-setting-input", size=200, min=0,
                                                                 max=1000, value=5)
                                            ],

                                        ),
                                        html.Br(),
                                        html.Div(
                                            id="power-factor-limit",
                                            className="usecase-line-row",
                                            children=[
                                                html.Label("Power Factor Limit", className="usecase-pfc-label"),
                                                daq.NumericInput(id="power-factor-limit-input",
                                                                 className="usecase-setting-input", size=200, min=0,
                                                                 max=1000, value=5)
                                            ],

                                        ),
                                        html.Br(),
                                        html.Div(
                                            id="control-type2",
                                            className="usecase-line-row",
                                            children=[
                                                html.Label("Control Type", className="usecase-pfc-label"),
                                                daq.BooleanSwitch(on=False, id="control-type-input21",
                                                                  className="usecase-switch", color="#cc3300",
                                                                  label="Optimization"),
                                                daq.BooleanSwitch(on=False, id="control-type-input22",
                                                                  className="usecase-switch", color="#cc3300",
                                                                  label="Rule-based"),

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
    return html.Div(
        id="configuration-select-menu-wrapper",
        children=[
            html.Div(
                id="configuration-select-menu",
                children=[
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
                            "Configure Usecase",  # html.Div(col, className="value-setter")
                        ],
                    ),
                    build_usecase_line("demand-charge-reduction", "Demand Charge Reduction", "switch_dcr", "dd_dcr",
                                       "dcr"),
                    html.Br(),
                    build_usecase_line("power-factor-correction", "Power Factor Correction", "switch_pfc", "dd_pfc",
                                       "pfc"),
                    html.Br(),
                    build_usecase_line("arbitrage", "Arbitrage", "switch_arb", "dd_arb", "arb"),
                    html.Br(),
                    build_usecase_line("revserves-placement", "Reserves Placement", "switch_rp", "dd_rp", "rp"),
                ]
            ),
            html.Br(),
            html.Br(),
            html.Div(
                id="dropdown-button",
                children=[html.Button("Update", className="", n_clicks=0), ]
            ),
        ]

    )


def build_settings_tab():
    """
    Function to put together the settings tab
    """
    return [
        # system_configuration_panel(),
        html.Div(
            id="system-configuration-menu",
            children=[configuration_panel(), data_upload_panel()],
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
                    html.Button(className="", id="button1", children="Arbitrage", n_clicks=0),
                    html.Button(className="", id="button1", children="Peak Shaving", n_clicks=0),
                    html.Button(className="", id="button1", children="Demand Shaping", n_clicks=0),
                    html.Button(className="", id="button1", children="System Capacity", n_clicks=0),
                    html.Button(className="", id="button1", children="Frequency Regulation", n_clicks=0),
                    html.Button(className="", id="button1", children="Spinning/Non-Spinning Reserve", n_clicks=0),
                    html.Button(className="", id="button1", children="Volt/Var", n_clicks=0),
                    html.Button(className="", id="button1", children="Co-optimize", n_clicks=0),
                ],
            ),
            html.Div(
                id="card-2",
                children=[

                    html.Button("Reset Live Updating", className="", id="button2", n_clicks=0),
                    daq.StopButton(id="stop-button", size=160, n_clicks=0),

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
                children=[
                    build_left_graph(),
                ]
            ),
            html.Div(
                id="right-graph",
                children=[
                    build_right_graph(),
                ]
            ),
        ],
    )


def build_left_graph():
    """
    function to build left graph
    Reference: https://plotly.com/python/subplots/
    """

    return html.Div(
        [dcc.Graph(id="left-graph-fig", animate=True),
         dcc.Interval(
             id='graph-update',
             interval=5000,
             n_intervals=0,
             disabled=True,
         ),

         ]
    )


def build_right_graph():
    """
    Function to build right graph
    Reference: https://plotly.com/python/line-charts/
    """

    return html.Div(
        [dcc.Graph(id="right-graph-fig", animate=True),
         dcc.Interval(
             id='graph-update',
             interval=5000,
             n_intervals=0,
             disabled=True,
         ),

         ]
    )


def revenue_block():
    return html.Div(
        id="revenue-block",
        children=[
            html.H6("Revenue"),
            html.Br(),
            html.Div(
                id="revenue-label1",
                children=[
                    html.Label("Day Ahead Estimate"),
                    dcc.Input(id="revenue1", type='text',disabled=True),
                ]
            ),

            html.Br(),
            html.Div(
                id="revenue-label2",
                children=[
                    html.Label("Actual, Not Adjusted"),
                    dcc.Input(id="revenue2", type='text',disabled=True),
                ]
            ),

            html.Br(),
            html.Div(
                id="revenue-label3",
                children=[
                    html.Label("Actual, Real Time Adjusted"),
                    dcc.Input(id="revenue3", type='text',disabled=True),
                ]
            ),

        ]
    )


def build_bottom_graph():
    return dcc.Graph(
        id="down-graph-fig", animate=True,
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
                id="left-graph",
                children=[
                    build_bottom_graph(),
                ]
            ),
            html.Div(
                id="bottom-panel-container",
                children=[
                    revenue_block(),
                ]
            ),
        ],
    )


def build_simulation_tab():
    """
    Function to put together the simulation  tab
    """
    return (html.Div(
        id="simulation-container",
        children=[
            build_buttons_panel(),
            html.Div(
                id="graphs-container",
                children=[build_top_panel(), build_bottom_panel()],
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



# Y.append(1)

# def dict_to_binary(the_dict):
#     str = dill.dumps(the_dict)
#     binary = ' '.join(format(ord(letter), 'b') for letter in str)
#     return binary

# def binary_to_dict(the_binary):
#     jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
#     d = dill.loads(jsn)
#     return d

def serve_layout():
    return html.Div(
        id="big-app-container",
        children=[
            build_banner(),
            dcc.Store(id="usecase-store", storage_type="session", data=init_usecase()),
            dcc.Store(id="gen-config-store", storage_type="session", data=init_gen_config()),
            dcc.Store(id="control-config-store", storage_type="session", data=init_control_config()),
            dcc.Store(id="data-config-store", storage_type="session", data=init_data_config()),
            dcc.Store(id="data-store", storage_type="session", data={}),
            dcc.Store(id="liveplot-store", storage_type="session", data={}),
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
    output=[Output("app-content", "children")],
    inputs=[Input("app-tabs", "value")],
    # state = [State("value-setter-store","data"), State("dropdown-store", "data")]
)
def render_tab_contents(tab_switch):
    """
    """
    if tab_switch == "tab2":
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
        # print(prop_id)
        if prop_id == "dcr" and button_click != 0:
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
        # print(prop_id)
        if prop_id == "pfc" and button_click != 0:
            return {"display": "block"}

    return {"display": "none"}


@app.callback(
    output=[Output("dd_dcr", "disabled"), Output("dd_pfc", "disabled"), Output("dd_arb", "disabled"),
            Output("dd_rp", "disabled"), \
            Output("dcr", "disabled"), Output("pfc", "disabled"), Output("arb", "disabled"), Output("rp", "disabled")],
    inputs=[Input("switch_dcr", "on"), Input("switch_pfc", "on"), Output("switch_arb", "on"),
            Output("switch_rp", "on")],
)
def make_usecase_active(s1, s2, s3, s4):
    print(s1)
    if s1 == True:
        d1a, d1b = False, False
    else:
        d1a, d1b = True, True
    if s2 == True:
        d2a, d2b = False, False
    else:
        d2a, d2b = True, True
    if s3 == True:
        d3a, d3b = False, False
    else:
        d3a, d3b = True, True
    if s4 == True:
        d4a, d4b = False, False
    else:
        d4a, d4b = True, True
    return [d1a, d2a, d3a, d4a, d1b, d2b, d3b, d4b]


@app.callback(
    [Output("graph-update", "disabled"), Output("stop-button", "buttonText")],
    [Input("stop-button", "n_clicks")],
    [State("graph-update", "disabled")],
)
def stop_production(n_clicks, current):
    if n_clicks == 0:
        return True, "start"
    return not current, "stop" if current else "start"


@app.callback(
    output=[Output("right-graph-fig", "figure"), Output("left-graph-fig", "figure"), Output("down-graph-fig", "figure"),
            Output("data-store", "data"), Output("liveplot-store", "data"), Output("revenue1","value"), Output("revenue2", "value"), Output("revenue3", "value")],
    inputs=[Input("graph-update", "n_intervals")],
    state=[State("data-store", "data"), State("liveplot-store", "data"), State("gen-config-store", "data"),
           State("data-config-store", "data"),
           State("usecase-store", "data")],)
# @cache.memoize
# fig1= None

def update_live_graph(ts, data1, live1, gen_config, data_config, use_case_library):
    '''
    updating the live graph
    '''
    def dash_fig(ts, prediction_data, actual_data, prediction_name, actual_name, **kwargs):
        dict_fig = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 350,
                    'xaxis_title': 'Seconds', 'yaxis_title': 'kW'}
        if kwargs:
            dict_fig.update(kwargs)
        legend_dict = dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x = [i for i in range(max(0, ts-20), (ts+1))],
            y = [prediction_data[0]] * (min(ts,20) +1),
            name=prediction_name))
        fig.add_trace(go.Scatter(
            x = [i for i in range(max(0, ts-20), (ts+1))],
            y = [i for i in deque(actual_data, maxlen= 20)],
            name=actual_name))

        # fig.add_trace(go.Scatter(
        #     x=[i for i in range(ts-20, ts+ 2)],
        #     y=[prediction_data[0]] * (ts + 2),
        #     name=prediction_name))
        # fig.add_trace(go.Scatter(
        #     x=[i for i in range(len(actual_data))],
        #     y=[i for i in actual_data],
        #     name=actual_name))

        ymin, ymax = min(prediction_data + actual_data), max(prediction_data + actual_data)
        fig.update_xaxes(range=[max(0, ts-20), ts], showline=True, linewidth=2, linecolor='#e67300', mirror=True)
        fig.update_yaxes(range=[ymin - 20, ymax + 20], showline=True, linewidth=2, linecolor='#e67300', mirror=True)
        # fig.update_yaxes(showline=True, linewidth=2, linecolor='#e67300', mirror=True)
        fig.update_layout(paper_bgcolor=dict_fig['linecolor'], width=dict_fig['width'], height=dict_fig['height'],
                          legend=legend_dict,
                          xaxis_title=dict_fig['xaxis_title'],
                          yaxis_title=dict_fig['yaxis_title'])
        return fig

    data = {}
    new_battery_setpoint = 0.0
    new_grid_load = 0.0
    new_SoC = 0.0
    new_battery_reactive_power = 0.0
    time_format = '%Y-%m-%d %H:%M:%S'
    start_time = gen_config['StartTime']
    end_time = gen_config['EndTime']
    battery_obj = battery_class_new(use_case_library, gen_config, data_config)

    if ts == 0:
        simulation_duration = int(
            (datetime.strptime(end_time, time_format) - datetime.strptime(start_time, time_format)).total_seconds())
        current_time = datetime.strptime(start_time, time_format)
        services_list = list(use_case_library.keys())
        priority_list = []
        for key, value in use_case_library.items():
            priority_list.append(use_case_library[key]["priority"])
        SoC_temp = battery_obj.SoC_init
        battery_obj.get_data()

    elif ts > 0:
        battery_obj.fromdict(live1)
        simulation_duration = data1["simulation_duration"]
        current_time = datetime.strptime(data1["current_time"], "%Y-%m-%d %H:%M:%S")
        services_list = data1["services_list"]
        priority_list = data1["priority_list"]
        SoC_temp = data1["SoC_temp"]

    print("SECOND IS", ts)

    if ts < simulation_duration:
        if ts % 3600 == 0:
            battery_obj.set_hourly_load_forecast(current_time, current_time + timedelta(days=1))
            battery_obj.DA_optimal_quantities()

        # if ((ts % battery_obj.reporting_frequency) == 0) and (ts > 1):
        #     idx = np.arange(0, 3600, 300)
        # battery_obj.metrics['Time'].append(ts)
        # battery_obj.metrics['arbitrage_revenue_da'].append(np.sum(
        #     np.multiply(np.array(da_variables['arbitrage_purchased_power_da'])[:, 0],
        #                 np.array(da_variables['price_predict_da'])[:, 0])))
        # metrics['arbitrage_revenue_ideal_rt'].append(np.sum(
        #     np.multiply(np.array(rt_variables['arbitrage_purchased_power_ideal_rt'])[:, idx],
        #                 np.array(rt_variables['price_actual_rt'])[:, idx])) * 5 / 60)
        # metrics['arbitrage_revenue_actual_rt'].append(np.sum(
        #     np.multiply(np.array(rt_variables['arbitrage_purchased_power_actual_rt'])[:, idx],
        #                 np.array(rt_variables['price_actual_rt'])[:, idx])) * 5 / 60)



        # current_peak_load_prediction = 0.0
        battery_obj.set_load_actual(battery_obj.load_predict[0])
        active_power_mismatch = battery_obj.actual_load[ts] - battery_obj.load_up[0]
        reactive_power_mismatch = battery_obj.load_pf * active_power_mismatch
        for i in range(len(services_list) - 1):
            service_priority = services_list[priority_list.index(i + 1)]
            if service_priority == "demand_charge":
                # check demand charge reduction in real-time
                new_SoC, new_battery_setpoint, new_grid_load = battery_obj.rtc_demand_charge_reduction \
                    (i, active_power_mismatch, battery_obj.battery_setpoints_prediction[0], SoC_temp,
                     battery_obj.actual_load[ts])

            elif service_priority == "power_factor_correction":
                if i == 0:  # highest priority
                    pass

                else:
                    battery_ratio = (1 - battery_obj.battery_react_power_prediction[0] / (
                            battery_obj.grid_react_power_prediction[0] + battery_obj.battery_react_power_prediction[
                        0]))

                    new_battery_reactive_power = battery_obj.battery_react_power_prediction[
                                                     0] + battery_ratio * reactive_power_mismatch
            else:
                check = 1
                # outage mitigation
                # active_power_mismatch  = battery_obj.actual_load[ts]
                #new_SoC, new_battery_setpoint, new_grid_load = battery_obj.outage_mitigation \
                #    (i, active_power_mismatch, battery_obj.battery_setpoints_prediction[0], SoC_temp,
                #     battery_obj.actual_load[ts])
    battery_obj.SoC_actual.append(SoC_temp)
    battery_obj.battery_setpoints_actual.append(new_battery_setpoint)
    battery_obj.grid_load_actual.append(new_grid_load)
    battery_obj.battery_react_power_actual.append(new_battery_reactive_power)
    battery_obj.grid_react_power_actual.append(battery_obj.load_pf * new_grid_load + new_battery_reactive_power)
    battery_obj.grid_apparent_power_actual.append(
        battery_obj.get_apparent_power(new_grid_load, battery_obj.grid_react_power_actual[ts]))
    battery_obj.grid_power_factor_actual.append(
        battery_obj.get_power_factor(new_grid_load, battery_obj.grid_apparent_power_actual[ts]))
    battery_obj.peak_load_actual.append(max(battery_obj.grid_load_actual[0:ts+1]))
    SoC_temp = new_SoC

    print(f"soc actual = {battery_obj.SoC_actual}")
    print(f"soc prediction = {battery_obj.SoC_prediction}")
    print(f"grid load actual = {battery_obj.grid_load_actual}")
    print(f"grid peak load prediction = {battery_obj.peak_load_prediction}")
    print(f"grid peak load actual = {max(battery_obj.peak_load_actual)}")
    # print(f"grid load actual 0:ts = {battery_obj.grid_load_actual[0:ts]}")
    # print(f"grid load actual max(0:ts) = {max(battery_obj.grid_load_actual[0:ts])}")

    battery_obj.metrics['peak_surcharge_da'].append(battery_obj.peak_load_prediction * battery_obj.peak_price)
    battery_obj.metrics['original_surcharge'].append(max(battery_obj.peak_load_actual) * battery_obj.peak_price)

    print('da surcharge' + str(battery_obj.metrics['peak_surcharge_da'][-1]))
    print('real time surcharge' + str(battery_obj.metrics['original_surcharge'][-1]))


    current_time = current_time + timedelta(seconds=+1)

    fig1_dict = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 500, 'height': 350,
                 'xaxis_title': 'Seconds', 'yaxis_title': 'kW'}
    fig1 = dash_fig(ts, battery_obj.SoC_prediction, battery_obj.SoC_actual,
                    "SoC Prediction", "SoC Actual", **fig1_dict)
    fig2 = dash_fig(ts, battery_obj.grid_load_prediction, battery_obj.grid_load_actual,
                    "Grid Load Prediction", "Grid Load Actual", **fig1_dict)

    fig3 = dash_fig(ts, [battery_obj.peak_load_prediction], battery_obj.peak_load_actual,
                    "Peak Load Prediction", "Peak Load Actual", **fig1_dict)

    fig4 = dash_fig(ts, battery_obj.grid_react_power_prediction, battery_obj.grid_react_power_actual,
                    "Grid Reactive Power Prediction", "Grid Reactive Power Actual",**fig1_dict)

    fig5 = dash_fig(ts, battery_obj.battery_react_power_prediction, battery_obj.battery_react_power_actual,
                    "Peak Reactive Power Prediction", "Peak Reactive Power Actual")

    data["SoC_temp"] = SoC_temp
    data["simulation_duration"] = simulation_duration
    data["services_list"] = services_list
    data["priority_list"] = priority_list
    data["current_time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    revenue1 = battery_obj.metrics['peak_surcharge_da'][-1]
    revenue2 = revenue1
    revenue3 = battery_obj.metrics['original_surcharge'][-1]

    live = battery_obj.todict()

    return [fig1, fig2, fig3, data, live, revenue1, revenue2, revenue3]


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
