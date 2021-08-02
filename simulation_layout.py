import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import plotly.graph_objects as go
from components.dropdown_graph import common_graph, common_slider

style = {'width': '100%', 'height': '30px', 'lineHeight': '30px', 'borderWidth': '1px', 'borderStyle': 'dashed',
         'borderRadius': '2px', 'textAlign': 'center', 'margin': '10px', 'fontSize': '12px'}
label_style = {'textAlign': 'center', 'fontSize': '16px'}
label_style_1 = {'textAlign': 'left', 'fontSize': '15px'}


def build_simulation_tab():
    """
    Function to put together the simulation  tab
    """
    return html.Div(
        id="simulation-container",
        className="simulation-container",
        children=[
            build_simulation_controls(),
            html.Div(
                id="graphs-container",
                className="graphs-container",
                children=[build_top_panel(), html.Br(), build_bottom_panel()],
            ),
        ]
    )


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


def build_simulation_input_controls():
    return html.Div(
        id="update-box-panel",
        className="button-panel",
        children=[
            html.Div(
                id="data_resolution",
                children=[
                    dcc.Input(id='update-data-resolution-box', type="number", min=1, max=3600, step=60, value=1,
                              className="input-number-box"),
                    html.Button('Data Resolution', id='submit-data-resolution', n_clicks=0,
                                className="button")
                ]),
            html.Div(
                id="start-timer",
                children=[
                    dcc.Input(id='start-time', type="number", min=0, max=5000, step=1, value=0),
                    html.Button('Start Time', id='submit-start-time', n_clicks=0, className="button")
                ]),
            html.Div(id="stop-timer",
                     children=[
                         dcc.Input(id='stop-time', type="number", min=0, max=3600 * 24, step=1, value=0),
                         html.Button('Stop Time', id='submit-stop-time', n_clicks=0, className="button")
                     ]),
            html.Div(id="rate",
                     children=[
                         dcc.Input(id='update-rate-box', type="number", min=800, max=5000, step=100, value=1000),
                         html.Button('Update Rate', id='submit-rate', n_clicks=0, className="button")
                     ]),
            html.Div(id="window",
                     children=[
                         dcc.Input(id='update-window', type="number", min=20, max=3600 * 24, step=10, value=120),
                         html.Button('Update Window', id='submit-update-window', n_clicks=0,
                                     className="button")
                     ]),
            html.Div(id="controller-update-rate",
                     children=[
                         dcc.Input(id='update-controller-rate-box', type="number", min=60, max=3600, step=60, value=60),
                         html.Button('Controller Update Rate', id='submit-controler-rate-update', n_clicks=0,
                                     className="button")
                     ]),
            # This will be for handling clicks on any of the buttons so they route properly to update the 
            # graphs
            html.Div(id='clicked-button', children='del:0 add:0 tog:0 last:nan', style={'display': 'none'})
        ])


def build_simulation_controls():
    """
    Function to generate a panel for buttons on left side
    """
    return html.Div(
        id="buttons-panel",
        className="simulation-container__buttons-panel",
        children=[
            build_simulation_input_controls(),
            html.Br(),
            common_slider(id="price-change-slider", className="price-change-slider", label_name="Price Change",
                          label_style=label_style),
            common_slider(id='grid-load-change-slider', className='grid-load-change-slider', label_name="Load Change",
                          label_style=label_style),
            html.Br(),
            build_unscheduled_outage_button(),
            html.Br(),
            build_external_signal_button(),
            html.Br(),
            revenue_block(),
            build_stop_button(),
        ],
    )


def revenue_block():
    return html.Div(
        [html.Label("Revenue", style=label_style),
         html.Div(
             id="revenue-block",
             className="row",
             children=[
                 html.Div(
                     id="revenue-label1",
                     children=[
                         html.Label("Day Ahead Estimate", style=label_style_1),
                         dcc.Input(id="revenue1", type='text', disabled=True, style={"width": '70%'}),
                     ]
                 ),

                 # html.Br(),
                 html.Div(
                     id="revenue-label2",
                     children=[
                         html.Label("Actual, Not Adjusted", style=label_style_1),
                         dcc.Input(id="revenue2", type='text', disabled=True, style={"width": '70%'}),
                     ]
                 ),

                 # html.Br(),
                 html.Div(
                     id="revenue-label3",
                     children=[
                         html.Label("Actual, Real Time Adjusted", style=label_style_1),
                         dcc.Input(id="revenue3", type='text', disabled=True, style={"width": '70%'}),
                     ]
                 ),

             ])])


def build_top_panel():
    """
    Function to build top panel for 2 graph placeholders
    TBD
    """

    return html.Div(
        id="top-section-container",
        className="graphs-container__row",
        children=[
            common_graph(id="top-left-graph"),
            common_graph(id="top-right-graph")
        ],
    )


def build_bottom_panel():
    """
    Function to build bottom panel for 2 graph placeholders
    TBD
    """
    return html.Div(
        id="bottom-section-container",
        className="graphs-container__row",
        children=[
            common_graph("bottom-left-graph", "GI"),
            common_graph("bottom-right-graph", "PL")
        ],
    )
