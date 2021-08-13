import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import plotly.graph_objects as go
from components.common import common_graph, common_slider, common_switch


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


def build_stop_button():
    return daq.StopButton(id="stop-button", n_clicks=0, className="stop-button", size=120)


def build_simulation_input_controls():
    return html.Div(
        id="update-box-panel",
        className="button-panel",
        children=[
            html.Div(
                id="data_resolution",
                children=[html.Button('Data Resolution', id='submit-data-resolution', n_clicks=0,
                                      className="button"),
                          dcc.Input(id='update-data-resolution-box', type="number", min=1, max=3600, step=60, value=1,
                                    className="input-number-box")
                          ]),
            html.Div(
                id="start-timer",
                children=[
                    html.Button('Start Time', id='submit-start-time', n_clicks=0, className="button"),
                    dcc.Input(id='start-time', type="number", min=0, max=5000, step=1, value=0)
                ]),
            html.Div(id="stop-timer",
                     children=[
                         html.Button('Stop Time', id='submit-stop-time', n_clicks=0, className="button"),
                         dcc.Input(id='stop-time', type="number", min=0, max=3600 * 24, step=1, value=0)
                     ]),
            html.Div(id="rate",
                     children=[
                         html.Button('Update Rate', id='submit-rate', n_clicks=0, className="button"),
                         dcc.Input(id='update-rate-box', type="number", min=800, max=5000, step=100, value=1000)
                     ]),
            html.Div(id="window",
                     children=[
                         html.Button('Update Window', id='submit-update-window', n_clicks=0,
                                     className="button"),
                         dcc.Input(id='update-window', type="number", min=20, max=3600 * 24, step=10, value=120)
                     ]),
            html.Div(id="controller-update-rate",
                     children=[
                         html.Button('Controller Update Rate', id='submit-controler-rate-update', n_clicks=0,
                                     className="button"),
                         dcc.Input(id='update-controller-rate-box', type="number", min=60, max=3600, step=60, value=60)
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
            common_slider(id="price-change-slider", className="price-change-slider", label_name="Price Change", ),
            common_slider(id='grid-load-change-slider', className='grid-load-change-slider',
                          label_name="Load Change", ),
            html.Br(), common_switch(id='outage-switch', label_name='Unschedule Outage'),
            html.Br(),
            common_switch(id='external-switch', label_name='Regulation Signal'),

            html.Br(),
            revenue_block(),
            html.Br(),
            build_stop_button(),
        ],
    )


def revenue_block():
    return html.Div(
        id="revenue-block",
        className="input-block",
        children=[
            html.Label("Revenue/ Cost Saving", className="input-block__title"),
            html.Div([html.Div(
                id="revenue-label1",
                className="input-block__row",
                children=[
                    html.Label("Day Ahead Estimate"),
                    dcc.Input(id="revenue1", type='text', disabled=True),
                ]
            ),

                html.Br(),
                html.Div(
                    id="revenue-label2",
                    className="input-block__row",
                    children=[
                        html.Label("Actual, Not Adjusted"),
                        dcc.Input(id="revenue2", type='text', disabled=True),
                    ]
                ),

                html.Br(),
                html.Div(
                    id="revenue-label3",
                    className="input-block__row",
                    children=[
                        html.Label("Actual, Real Time Adjusted"),
                        dcc.Input(id="revenue3", type='text', disabled=True),
                    ]
                )], className="input-block__rows"),

        ])


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
