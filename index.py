from app import *
import dash
import base64
import io
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
# import dash_bootstrap_components as dbc
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
from plotly.subplots import make_subplots

style = {'width': '100%', 'height': '30px', 'lineHeight': '30px', 'borderWidth': '1px', 'borderStyle': 'dashed',
         'borderRadius': '2px', 'textAlign': 'center', 'margin': '10px', 'fontSize': '12px'}
label_style = {'textAlign': 'center'}
interval = 1000
click = 0
dcc_interval = dcc.Interval(
    id='graph-update',
    interval=interval,
    n_intervals=0,
    disabled=True, )

@app.callback(
    Output('graph-update', 'interval'),
    [Input('submit-val', 'n_clicks')],
    [State('update-rate-box', 'value')])
def update_output(n_clicks, value):
    return value


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


def upload_file(id):
    return dcc.Upload(id=id,
                      children=html.Div(
                          ["Drag and drop or select a file"]),
                      # style=style
                      )


def dcc_date_picker():
    return dcc.DatePickerRange(
        start_date_placeholder_text="Start Period",
        end_date_placeholder_text="End Period", )


def data_upload_panel():
    return html.Div(
        id="configuration-select-menu-wrapper",
        children=[
            html.Div(
                id="configuration-select-menu",
                children=[
                    html.H6("Upload"),
                    html.Br(),
                    html.Div(
                        id="dropdown-label",
                        children=[
                            html.Div(
                                children=[
                                    html.Label("Load Profile Data"),
                                    dcc_date_picker(),
                                    upload_file("upload-load-profile-data")
                                ]
                            ),
                            html.Hr(),
                        ]
                    ),
                    # html.Br(),
                    # html.Div(id='output-upload-load-profile-data'),
                    html.Br(),
                    html.Div(
                        id="dropdown-label",
                        children=[
                            html.Div(
                                children=[
                                    html.Label("Energy Price Data"),
                                    dcc_date_picker(),
                                    upload_file("upload-energy-price-data")
                                ]
                            ),
                            html.Hr(),
                            # html.Div(id='output-upload-cable-data'),
                        ]
                    ),
                    # html.Br(),
                    # html.Div(id='output-upload-energy-price-data'),
                    html.Br(),
                    html.Div(
                        id="dropdown-label",
                        children=[
                            html.Div(
                                children=[
                                    html.Label("ESS Data"),
                                    upload_file("upload-ess-data")
                                ]
                            ),
                            html.Hr(),
                            # html.Div(id='output-upload-cable-data'),
                        ]
                    ),
                    # html.Div(id='output-upload-ess-data'),

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
                                        dcc.Dropdown(
                                            id='variable-dcr-dropdown',
                                            options=[
                                                {'label': 'Grid Import', 'value': 'GI'},
                                                {'label': 'Peak Load', 'value': 'PL'}
                                            ],
                                            value='GL'
                                        ),
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
                                        dcc.Dropdown(
                                            id='variable-pfc-dropdown',
                                            options=[
                                                {'label': 'Power Factor', 'value': 'PF'},
                                                {'label': 'Reactive Grid Power', 'value': 'RGP'},
                                                {'label': 'Reactive Battery Power', 'value': 'RBL'}
                                            ],
                                            value='PF'
                                        ),
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


def build_price_change_button():
    return html.Div(
        id="card-1",
        children=[html.Button("Price change in load", className="", id="button1", n_clicks=0),
                  # html.Div(id='price-change-button'),
                  ],
    )


def build_price_change_slider():
    return html.Div([
        html.Label('Price Change', style=label_style),
        dcc.Slider(
            id='price-change-slider',
            min=-100,
            max=100,
            step=20,
            marks={
                -100: '-100 %',
                -75: '-75 %',
                -50: '-50 %',
                -25: '-25 %',
                0: '0 %',
                25: '25 %',
                50: '50 %',
                75: '75 %',
                100: '100 %'
            },
            value=0,
            updatemode='drag'
        ),
        # html.Div(id='slider-output-container')
    ])


def grid_load_change_slider():
    return html.Div([
        html.Label('Load Change', style=label_style),
        dcc.Slider(
            id='grid-load-change-slider',
            min=-100,
            max=100,
            step=20,
            marks={
                -100: '-100 %',
                -75: '-75 %',
                -50: '-50 %',
                -25: '-25 %',
                0: '0 %',
                25: '25 %',
                50: '50 %',
                75: '75 %',
                100: '100 %'
            },
            value=0,
            updatemode='drag'
        ),
        # html.Div(id='slider-output-container')
    ])


def build_unscheduled_outage_button():
    return html.Div([
        html.Label('Unschedule Outage', style=label_style),
        daq.ToggleSwitch(
            id='outage-switch',
            label=['OFF', 'ON'],
            labelPosition='bottom',
            color='green',
            value=False
        ),
        # html.Div(id='Unscheduled-outage-button'),
    ],
    )


def build_stop_button():
    return html.Div(
        id="card-3",
        children=[
            # html.Button("Reset Live Updating", className="", id="button3", n_clicks=0),
            daq.StopButton(id="stop-button", label='Reset Live Updating', labelPosition='top', size=160, n_clicks=0),
        ],
    )


def build_update_buffer_button():
    return html.Div([
        dcc.Input(
            id='update-buffer',
            type="number",
            min=200,
            max=5000,
            step=100,
            value=2000
        ),
        html.Button('Update Buffer Size', id='update-buffer-button', n_clicks=0),
    ]
    )


def build_update_rate_box():
    return html.Div([
        dcc.Input(
            id='update-rate-box',
            type="number",
            min=800,
            max=5000,
            step=100,
            value=1000
        ),
        html.Button('Update Rate', id='submit-val', n_clicks=0),
        # html.Div(id='slider-output-container')
    ])


def build_update_window_box():
    return html.Div([
        dcc.Input(
            id='update-window',
            type="number",
            min=20,
            max=1000,
            step=10,
            value=50
        ),
        html.Button('Update Window', id='submit-val', n_clicks=0),
        # html.Div(id='slider-output-container')
    ])


def build_update_boxes():
    return html.Div(
        id="update-box-panel",
        className="row",
        children=[
            # build_update_rate_button(),
            html.Div(id="rate", children=[build_update_rate_box()]),
            html.Div(id="window", children=[build_update_window_box()])
            # html.Div(id="buffer", children=[build_update_buffer_button()])
        ])


def build_buttons_panel():
    """
    Function to generate a panel for buttons on left side
    """
    return html.Div(
        id="buttons-panel",
        className="row",
        children=[
            build_update_boxes(),
            html.Br(),
            build_price_change_slider(),
            grid_load_change_slider(),
            html.Br(),
            build_unscheduled_outage_button(),
            # build_unschedule_outage_slider(),
            html.Br(),
            build_stop_button()
        ],

    )


def build_left_graph():
    """
    function to build left graph
    Reference: https://plotly.com/python/subplots/
    """
    return html.Div(
        [dcc.Graph(id="left-graph-fig", animate=True),
         dcc_interval
         ]
    )


def build_right_graph():
    return html.Div(
        [dcc.Graph(id="right-graph-fig", animate=True),
         dcc_interval
         ]
    )


def build_left_dropdown_box():
    return html.Div([
        # html.Button('Update Rate', id='submit-val', n_clicks=0),
        html.Label('Left y-axis', style=label_style),
        dcc.Dropdown(
            id='fig-left-dropdown',
            options=[
                {'label': 'Grid Import', 'value': 'GI'},
                {'label': 'Peak Load', 'value': 'PL'},
                {'label': 'Grid Reactive', 'value': 'GR'},
                {'label': 'Battery Reactive', 'value': 'BR'},
                {'label': 'Power Factor', 'value': 'PF'},
                {'label': 'Energy Price', 'value': 'EP'},
                {'label': 'Demand', 'value': 'D'}
            ],
            #placeholder="Left y-axis (default = Grid Import)",
            value='GI'
        ),
        # html.Div(id='slider-output-container')
    ],style=dict(width='30%'))


def build_right_dropdown_box():
    return html.Div([
        # html.Button('Update Rate', id='submit-val', n_clicks=0),
        html.Label('Right y-axis', style=label_style),
        dcc.Dropdown(
            id='fig-right-dropdown',
            options=[
                {'label': 'Grid Import', 'value': 'GI'},
                {'label': 'Peak Load', 'value': 'PL'},
                {'label': 'Grid Reactive', 'value': 'GR'},
                {'label': 'Battery Reactive', 'value': 'BR'},
                {'label': 'Power Factor', 'value': 'PF'},
                {'label': 'Energy Price', 'value': 'EP'},
                {'label': 'Demand', 'value': 'D'}
            ],
            #placeholder="Right y-axis (default = Peak Load)",
            value='PL'
        ),
        # html.Div(id='slider-output-container')
    ], style={"width": '30%', "margin-left": "150px"})


def build_bottom_graph():
    return html.Div([html.Div(id="dropdown", className="row",
        children=[build_left_dropdown_box(), build_right_dropdown_box()],
                              style= dict(display='flex'),),
                     dcc.Graph(id="down-graph-fig", animate=True),
                     dcc_interval
                     ])


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
                    dcc.Input(id="revenue1", type='text', disabled=True),
                ]
            ),
            html.Br(),
            html.Div(
                id="revenue-label2",
                children=[
                    html.Label("Actual, Not Adjusted"),
                    dcc.Input(id="revenue2", type='text', disabled=True),
                ]
            ),

            html.Br(),
            html.Div(
                id="revenue-label3",
                children=[
                    html.Label("Actual, Real Time Adjusted"),
                    dcc.Input(id="revenue3", type='text', disabled=True),
                ]
            ),

        ]
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
    if tab_switch == "tab1":
        return build_settings_tab()
    return build_simulation_tab()


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


# @app.callback(
#     [Output("Simulate Power Outage", "disabled"), Output("Power-Outage-button", "buttonText")],
#     [Input("", "n_clicks")],
#     #[State("graph-update", "disabled")],
# )
# def power_outage(n_clicks, current):
#     if n_clicks == 0:
#         return True, "start"
#     return not current, "stop" if current else "start"


@app.callback(
    output=[Output("right-graph-fig", "figure"), Output("left-graph-fig", "figure"), Output("down-graph-fig", "figure"),
            Output("data-store", "data"), Output("liveplot-store", "data"), Output("revenue1", "value"),
            Output("revenue2", "value"), Output("revenue3", "value")],
    inputs=[Input("graph-update", "n_intervals"), Input("outage-switch", "value"), Input("submit-val", "n_clicks")],
    state=[State('price-change-slider', 'value'), State('grid-load-change-slider', 'value'),
           State('update-window', 'value'), State('fig-left-dropdown', 'value'), State('fig-right-dropdown', 'value'),
           State("data-store", "data"), State("liveplot-store", "data"), State("gen-config-store", "data"),
           State("data-config-store", "data"), State("usecase-store", "data")])
# @cache.memoize
# fig1= None

def update_live_graph(ts, outage_flag, submit_click, price_change_value, grid_load_change_value, update_window,
                      fig_leftdropdown, fig_rightdropdown, data1, live1,
                      gen_config, data_config,
                      use_case_library):
    '''
    updating the live graph
    '''
    print(f"outage flag = {outage_flag}")
    print(f"price change value = {price_change_value}")
    print(f"grid load change value = {grid_load_change_value}")
    update_buffer = 2000

    print(f"left dropdown = {fig_leftdropdown}")
    print(f"right dropdown = {fig_rightdropdown}")

    def dash_fig_multiple_yaxis(ts, prediction_data, actual_data, prediction_data_2, actual_data_2, title=None,
                                **kwargs):
        y_axis_left_margin = 20
        y_axis_right_margin = 20

        dict_fig = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                    'xaxis_title': 'Seconds', 'yaxis_title': 'kW'}
        if fig_leftdropdown == 'EP':
            y_axis_left_margin = 0.01
        if fig_rightdropdown == 'EP':
            y_axis_right_margin = 0.01

        if kwargs:
            dict_fig.update(kwargs)
        legend_dict = dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
        # fig = go.Figure()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=[i for i in range(max(0, ts - update_buffer), (ts + 1))],
            y=[prediction_data[0]] * (min(ts, update_buffer) + 2),
            name="Prediction", mode='lines + markers'), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=[i for i in range(max(0, ts - update_buffer), (ts + 1))],
            y=[prediction_data_2[0]] * (min(ts, update_buffer) + 2),
            name="Prediction", mode='lines'), secondary_y=True)

        fig.add_trace(go.Scatter(
            x=[i for i in range(max(0, ts - update_buffer), (ts + 1))],
            y=[i for i in deque(actual_data, maxlen=update_buffer)],
            name="Actual",mode='lines + markers'), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=[i for i in range(max(0, ts - update_buffer), (ts + 1))],
            y=[i for i in deque(actual_data_2, maxlen=update_buffer)],
            name="Actual", mode='lines'), secondary_y=True)

        ymin, ymax = min([prediction_data[0]] + actual_data), max([prediction_data[0]] + actual_data)
        ymin_2, ymax_2 = min([prediction_data_2[0]] + actual_data_2), max([prediction_data_2[0]] + actual_data_2)
        fig.update_xaxes(range=[max(0, ts - update_window), ts], showline=True, linewidth=2, linecolor='#e67300',
                         mirror=True, title_text="Seconds")
        fig.update_yaxes(range=[ymin - y_axis_left_margin, ymax + y_axis_left_margin], showline=True, linewidth=2, linecolor='#e67300',
                         mirror=True, secondary_y=False, title_text="kW")
        fig.update_yaxes(range=[ymin_2 - y_axis_right_margin, ymax_2 + y_axis_right_margin], showline=True, linewidth=2, linecolor='#e67300',
                         mirror=True, secondary_y=True, title_text="kW")
        # fig.update_yaxes(showline=True, linewidth=2, linecolor='#e67300', mirror=True)
        fig.update_layout(paper_bgcolor=dict_fig['linecolor'], width=dict_fig['width'], height=dict_fig['height'],
                          legend=legend_dict, showlegend=True, title=title)

        return fig

    def dash_fig(ts, prediction_data, actual_data, title=None, **kwargs):
        dict_fig = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                    'xaxis_title': 'Seconds', 'yaxis_title': 'kW'}
        if kwargs:
            dict_fig.update(kwargs)
        legend_dict = dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[i for i in range(max(0, ts - update_buffer), (ts + 1))],
            y=[prediction_data[0]] * (min(ts, update_buffer) + 2),
            name="Prediction"))
        fig.add_trace(go.Scatter(
            x=[i for i in range(max(0, ts - update_buffer), (ts + 1))],
            y=[i for i in deque(actual_data, maxlen=update_buffer)],
            name="Actual"))

        ymin, ymax = min([prediction_data[0]] + actual_data), max([prediction_data[0]] + actual_data)

        fig.update_xaxes(range=[max(0, ts - update_window), ts], showline=True, linewidth=2, linecolor='#e67300',
                         mirror=True)
        fig.update_yaxes(range=[ymin - 20, ymax + 20], showline=True, linewidth=2, linecolor='#e67300', mirror=True)
        # fig.update_yaxes(showline=True, linewidth=2, linecolor='#e67300', mirror=True)
        fig.update_layout(paper_bgcolor=dict_fig['linecolor'], width=dict_fig['width'], height=dict_fig['height'],
                          legend=legend_dict, showlegend=True, title=title,
                          xaxis_title=dict_fig['xaxis_title'],
                          yaxis_title=dict_fig['yaxis_title'])

        return fig

    data = {}
    new_battery_setpoint = 0.0
    new_grid_load = 0.0
    new_grid_reactive_power = 0.0
    new_SoC = 0.0
    new_battery_reactive_power = 0.0
    time_format = '%Y-%m-%d %H:%M:%S'
    start_time = gen_config['StartTime']
    end_time = gen_config['EndTime']
    battery_obj = battery_class_new(use_case_library, gen_config, data_config)

    if ts == 0:
        print('at ts=0')
        simulation_duration = int(
            (datetime.strptime(end_time, time_format) - datetime.strptime(start_time, time_format)).total_seconds())
        current_time = datetime.strptime(start_time, time_format)
        # next_day_hourly_interval = timedelta(days=+1)
        # day_ahead_forecast_horizon = current_time + next_day_hourly_interval

        services_list = list(use_case_library.keys())
        priority_list = []
        for key, value in use_case_library.items():
            priority_list.append(use_case_library[key]["priority"])
        SoC_temp = battery_obj.SoC_init
        battery_obj.get_data()
        print('SoC Temp'+str(SoC_temp))
        # price_temp = 0.0
    elif ts > 0:
        print('at ts>0')
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
            print("just before price forecast")
            battery_obj.set_hourly_price_forecast(current_time, current_time + timedelta(days=1), ts)
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
        print(f"price predict = {battery_obj.price_predict[0]}")
        battery_obj.set_load_actual(battery_obj.load_predict[0], np.mean(np.diff(battery_obj.load_predict[0:3])) * battery_obj.hrs_to_secs )

        # if (ts % 300 == 0):
        battery_obj.set_price_actual(battery_obj.price_predict[0],
                                     (battery_obj.price_predict[1] - battery_obj.price_predict[0]) * 300 * battery_obj.hrs_to_secs, ts)

        # change price and load values given there is a user input to change it
        battery_obj.actual_price[ts] = max(0.0001, battery_obj.actual_price[ts] + battery_obj.actual_price[ts] * price_change_value / 100)
        battery_obj.actual_load[ts] = max(0, battery_obj.actual_load[ts] + battery_obj.actual_load[ts] * (
                    grid_load_change_value / 100))

        if outage_flag:
            check = 1
            # outage mitigation
            active_power_mismatch = battery_obj.actual_load[ts]
            # new_SoC, new_battery_setpoint, new_grid_load = battery_obj.outage_mitigation \
            #     (active_power_mismatch, battery_obj.battery_setpoints_prediction[0], SoC_temp,
            #      battery_obj.actual_load[ts])
            new_battery_setpoint = battery_obj.change_setpoint(0, active_power_mismatch)
            # check SoC
            new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, SoC_temp)
            # new grid load
            new_grid_load = battery_obj.actual_load[ts] - new_battery_setpoint
            # print(f"New Battery Setpoint in outage block = {new_battery_setpoint}")
            # print(f"New grid load = {new_grid_load}")
            # print(f"New actual load = {battery_obj.actual_load[ts]}")
            reactive_power_mismatch = battery_obj.load_pf * active_power_mismatch
            new_battery_reactive_power = -reactive_power_mismatch
            new_grid_reactive_power = 0.0
        else:
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
                        new_grid_reactive_power = battery_obj.load_pf * new_grid_load + new_battery_reactive_power

    battery_obj.SoC_actual.append(SoC_temp)
    battery_obj.battery_setpoints_actual.append(new_battery_setpoint)
    battery_obj.grid_load_actual.append(new_grid_load)
    battery_obj.battery_react_power_actual.append(new_battery_reactive_power)

    # battery_obj.grid_react_power_actual.append(battery_obj.load_pf * new_grid_load + new_battery_reactive_power)

    battery_obj.grid_react_power_actual.append(new_grid_reactive_power)

    battery_obj.grid_apparent_power_actual.append(
        battery_obj.get_apparent_power(new_grid_load, battery_obj.grid_react_power_actual[ts]))
    battery_obj.grid_power_factor_actual.append(
        battery_obj.get_power_factor(new_grid_load, battery_obj.grid_apparent_power_actual[ts]))
    battery_obj.peak_load_actual.append(max(battery_obj.grid_load_actual[0:ts + 1]))
    SoC_temp = new_SoC
    # price_temp = battery_obj.actual_price[ts]
    # print(f"New Battery Setpoint after outage block = {new_battery_setpoint}")
    # print(f"soc actual = {battery_obj.SoC_actual}")
    # print(f"soc prediction = {battery_obj.SoC_prediction}")
    print(f"grid load new = {new_grid_load}")
    print(f"grid load reactive = {new_grid_reactive_power}")
    print(f"energy price = {battery_obj.actual_price}")

    # print(f"grid peak load prediction = {battery_obj.peak_load_prediction}")
    # print(f"grid peak load actual = {max(battery_obj.peak_load_actual)}")
    # print(f"Battery Setpoints Prediction = {battery_obj.battery_setpoints_prediction}")

    # print(f"Battery Setpoints Actual = {battery_obj.battery_setpoints_actual}")
    # print(f"grid load actual 0:ts = {battery_obj.grid_load_actual[0:ts]}")
    # print(f"grid load actual max(0:ts) = {max(battery_obj.grid_load_actual[0:ts])}")

    battery_obj.metrics['peak_surcharge_da'].append(battery_obj.peak_load_prediction * battery_obj.peak_price)
    battery_obj.metrics['original_surcharge'].append(max(battery_obj.peak_load_actual) * battery_obj.peak_price)

    # print('da surcharge' + str(battery_obj.metrics['peak_surcharge_da'][-1]))
    # print('real time surcharge' + str(battery_obj.metrics['original_surcharge'][-1]))

    current_time = current_time + timedelta(seconds=+1)

    fig_dict = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                'xaxis_title': 'Seconds', 'yaxis_title': 'kW'}
    fig_soc_dict = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                    'xaxis_title': 'Seconds', 'yaxis_title': 'kWh'}
    fig1 = dash_fig(ts, battery_obj.SoC_prediction, battery_obj.SoC_actual,
                    "SoC", **fig_soc_dict)
    fig2 = dash_fig(ts, battery_obj.battery_setpoints_prediction, battery_obj.battery_setpoints_actual,
                    "Battery Setpoint", **fig_dict)

    print(f"price predict = {battery_obj.price_predict}")

    fig_obj = {"PL": [[battery_obj.peak_load_prediction], battery_obj.peak_load_actual],
               "GR": [battery_obj.grid_react_power_prediction, battery_obj.grid_react_power_actual],
               "BR": [battery_obj.battery_react_power_prediction, battery_obj.battery_react_power_actual],
               "GI": [battery_obj.grid_load_prediction, battery_obj.grid_load_actual],
               "EP": [battery_obj.price_predict, battery_obj.actual_price]}
    # fig_leftdropdown == "GI" if fig_leftdropdown is None else fig_leftdropdown
    # fig_rightdropdown == "PL" if fig_rightdropdown is None else fig_rightdropdown
    fig3 = dash_fig_multiple_yaxis(ts, fig_obj[fig_leftdropdown][0], fig_obj[fig_leftdropdown][1],
                                   fig_obj[fig_rightdropdown][0], fig_obj[fig_rightdropdown][1], **fig_dict)


    data["SoC_temp"] = SoC_temp
    data["simulation_duration"] = simulation_duration
    data["services_list"] = services_list
    data["priority_list"] = priority_list
    data["current_time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    revenue1 = round(battery_obj.metrics['peak_surcharge_da'][-1], 2)
    revenue2 = revenue1
    revenue3 = round(battery_obj.metrics['original_surcharge'][-1], 2)

    live = battery_obj.todict()

    return [fig1, fig2, fig3, data, live, revenue1, revenue2, revenue3]


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
