import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq


def build_settings_tab():
    """
    Function to put together the settings tab
    """
    return html.Div(
            id="system-configuration-menu",
            children=[configuration_panel(), data_upload_panel()],
        )


def dcc_date_picker():
    return dcc.DatePickerRange(
        start_date_placeholder_text="Start Period",
        end_date_placeholder_text="End Period", )


def upload_file(id):
    return dcc.Upload(id=id,
                      children=html.Div(
                          ["Drag and drop or select a file"]),
                      # style=style
                      )


def data_upload_panel():
    return html.Div(
        id="data-upload-select-menu-wrapper",
        children=[
            html.Div(
                id="data-upload-select-menu",
                children=[
                    html.H6("Upload"),
                    html.Br(),
                    html.Div(
                        id="data-upload-dropdown-label-profile",
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
                        id="data-upload-dropdown-label-energy-prices",
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
                        id="data-upload-dropdown-label-ess-data",
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
            usecase_dcr_popup(),
            usecase_pfc_popup(),
        ]

    )