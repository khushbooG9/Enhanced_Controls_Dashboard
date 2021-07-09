import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import plotly.graph_objects as go

style = {'width': '100%', 'height': '30px', 'lineHeight': '30px', 'borderWidth': '1px', 'borderStyle': 'dashed',
         'borderRadius': '2px', 'textAlign': 'center', 'margin': '10px', 'fontSize': '12px'}
label_style = {'textAlign': 'center',  'fontSize': '16px'}
label_style_1 = {'textAlign': 'left',  'fontSize': '15px'}



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

def build_external_signal_button():
    return html.Div([
        html.Label('Regulation Signal', style=label_style),
        daq.ToggleSwitch(
            id='external-switch',
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
            daq.StopButton(id="stop-button", labelPosition='top', size=160, n_clicks=0),
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


def build_controller_update_rate_box():
    return html.Div([
        dcc.Input(
            id='update-controller-rate-box',
            type="number",
            min=60,
            max=3600,
            step=60,
            value=60
        ),
        html.Button('Controller Update Rate', id='submit-val', n_clicks=0),
        # html.Div(id='slider-output-container')
    ])


def build_data_resolution_box():
    return html.Div([
        dcc.Input(
            id='update-data-resolution-box',
            type="number",
            min=1,
            max=3600,
            step=60,
            value=1
        ),
        html.Button('Data Resolution', id='submit-val', n_clicks=0),
        # html.Div(id='slider-output-container')
    ])


def build_start_timer_box():
    return html.Div([
        dcc.Input(
            id='start-time',
            type="number",
            min=0,
            max=5000,
            step=1,
            value=0
        ),
        html.Button('Start Time', id='submit-val', n_clicks=0),
        # html.Div(id='slider-output-container')
    ])


def build_stop_timer_box():
    return html.Div([
        dcc.Input(
            id='stop-time',
            type="number",
            min=0,
            max=3600*24,
            step=1,
            value=0
        ),
        html.Button('Stop Time', id='submit-val', n_clicks=0),
        # html.Div(id='slider-output-container')
    ])


def build_update_window_box():
    return html.Div([
        dcc.Input(
            id='update-window',
            type="number",
            min=20,
            max=3600*24,
            step=10,
            value=120
        ),
        html.Button('Update Window', id='submit-val', n_clicks=0),
        # html.Div(id='slider-output-container')
    ])


def build_update_boxes():
    return html.Div(
        id="update-box-panel",
        className="row",
        children=[
            html.Div(id="data_resolution", children=[build_data_resolution_box()]),
            html.Div(id="start-timer", children=[ build_start_timer_box()]),
            html.Div(id="stop-timer", children=[build_stop_timer_box()]),
            html.Div(id="rate", children=[build_update_rate_box()]),
            html.Div(id="window", children=[build_update_window_box()]),
            html.Div(id="controller-update-rate", children=[build_controller_update_rate_box()]),
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
            html.Br(),
            build_external_signal_button(),
            html.Br(),
            #html.Br(),
            ess_parameter_block_1(),
            ess_parameter_block_2(),
            revenue_block(),
            build_stop_button(),
        ],
    )


def revenue_block():
    return html.Div(
        [html.Label("Revenue", style=label_style),
        html.Div(
        id="revenue-block",
        className= "row",
        children=[
            #html.Br(),
            html.Div(
                id="revenue-label1",
                children=[
                    html.Label("Day Ahead Estimate", style=label_style_1),
                    dcc.Input(id="revenue1", type='text', disabled=True, style={"width": '70%'}),
                ]
            ),

            #html.Br(),
            html.Div(
                id="revenue-label2",
                children=[
                    html.Label("Actual, Not Adjusted", style=label_style_1),
                    dcc.Input(id="revenue2", type='text', disabled=True, style={"width": '70%'}),
                ]
            ),

            #html.Br(),
            html.Div(
                id="revenue-label3",
                children=[
                    html.Label("Actual, Real Time Adjusted", style=label_style_1),
                    dcc.Input(id="revenue3", type='text', disabled=True, style={"width": '70%'}),
                ]
            ),

        ])])


def ess_parameter_block_1():
    return html.Div(
        [html.Label("ESS Parameter", style=label_style),
        html.Div(
        id="ess-parameter-block",
        className= "row",
        children=[
            #html.Br(),
            html.Div([html.Label("Max SoC %", style=label_style_1),
                      dcc.Input( id='max-soc',
                                type="number",
                                min=50,
                                max=100,
                                step=10,
                                value=90,
                                style={"width": '70%'}
                            )]),

            html.Div([html.Label("Min SOC %", style=label_style_1),
                      dcc.Input( id='min-soc',
                                type="number",
                                min=0,
                                max=50,
                                step=10,
                                value=10,
                                style={"width": '70%'}
                            )]),

        ])])


def ess_parameter_block_2():
    return html.Div(
        [#html.Label("ESS Parameter", style=label_style),
        html.Div(
        id="ess-parameter-block",
        className= "row",
        children=[
            html.Div([html.Label("Energy Capacity kWh", style=label_style_1),
                      dcc.Input(id='energy-capacity',
                                type="number",
                                min=100,
                                max=2000,
                                step=100,
                                value=1500,
                                style={"width": '70%'}
                                )]),

            html.Div([html.Label("Max Power kW", style=label_style_1),
                      dcc.Input(id='max-power',
                                type="number",
                                min=100,
                                max=1000,
                                step=50,
                                value=750,
                                style={"width": '70%'}
                                )]),

        ])])

def build_top_panel():
    """
    Function to build top panel for 2 graph placeholders
    TBD
    """

    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            common_graph(id="top-left-graph"),
        ],
    )


def build_bottom_panel():
    """
    Function to build bottom panel for 2 graph placeholders
    TBD
    """
    return html.Div(
        id="bottom-section-container",
        className="row",
        children=[
            common_graph("bottom-left-graph", "GI"),
            common_graph("bottom-right-graph", "PL")
        ],
    )
