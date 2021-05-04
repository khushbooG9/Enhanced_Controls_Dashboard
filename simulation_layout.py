import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq

style = {'width': '100%', 'height': '30px', 'lineHeight': '30px', 'borderWidth': '1px', 'borderStyle': 'dashed',
         'borderRadius': '2px', 'textAlign': 'center', 'margin': '10px', 'fontSize': '12px'}
label_style = {'textAlign': 'center',  'fontSize': '16px'}
label_style_1 = {'textAlign': 'left',  'fontSize': '15px'}
interval = 1000
click = 0
dcc_interval = dcc.Interval(
    id='graph-update',
    interval=interval,
    n_intervals=0,
    disabled=True, )


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
            html.Br(),
            build_external_signal_button(),
            html.Br(),
            revenue_block(),
            #html.Br(),
            build_stop_button(),
        ],
    )


def build_left_dropdown_box():
    return dcc.Dropdown(
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
        )


def build_right_dropdown_box():
    return dcc.Dropdown(
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
            #placeholder="Left y-axis (default = Grid Import)",
            value='PL',
        )
    #style={"width": '30%', "margin-left": "150px"})

def build_left_graph():
    """
    function to build left graph
    Reference: https://plotly.com/python/subplots/
    """
    return html.Div([dcc.Graph(id="left-graph-fig", animate=True),
                     dcc_interval])


def build_right_graph():
    return html.Div([dcc.Graph(id="right-graph-fig", animate=True),
                     dcc_interval])


def build_left_bottom_graph():
    return html.Div([build_left_dropdown_box(),
                    dcc.Graph(id="down-left-graph", animate=True),
                    dcc_interval])


def build_right_bottom_graph():
    return html.Div([build_right_dropdown_box(),
                     dcc.Graph(id="down-right-graph", animate=True),
                     dcc_interval])


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
    Function to build bottom panel for 2 graph placeholders
    TBD
    """
    return html.Div(
        id="bottom-section-container",
        className="row",
        children=[
            html.Div(
                id="left-graph",
                children=[
                    build_left_bottom_graph(),
                ]
            ),
            html.Div(
                id="right-graph",
                children=[
                    build_right_bottom_graph(),
                ]
            ),
        ],
    )
