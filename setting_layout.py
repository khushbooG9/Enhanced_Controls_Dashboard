import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html


def build_settings_tab():
    """
    Function to put together the settings tab
    """
    return html.Div(
        className="settings-container",
        id="settings-container",
        children=[configuration_panel(), data_upload_panel()],
    )


def dcc_date_picker():
    return html.Div(dcc.DatePickerRange(
        start_date_placeholder_text="Start Period",
        end_date_placeholder_text="End Period", ), className="upload__date-picker")


def upload_file(id):
    return dcc.Upload(id=id,
                      children=html.Label("Drag and drop or select a file", htmlFor="file"),
                      className="upload__file"
                      )


def data_upload_panel():
    return html.Div(
        className="settings-container__upload__wrapper",
        id="data-upload-select-menu-wrapper",
        children=[
            html.Div(
                id="data-upload-select-menu",
                className="settings-container__upload",
                children=[
                    html.Div(
                        className="upload",
                        children=[
                            html.H6("Upload"),
                            html.Br(),
                            html.Div(
                                id="data-upload-dropdown-label-profile",
                                children=[
                                    html.Div(
                                        className="upload__row",
                                        children=[
                                            html.Label("Load Profile Data"),
                                            dcc_date_picker(),
                                            upload_file("upload-load-profile-data")
                                        ]
                                    ),
                                ]
                            ),
                            html.Br(),
                            html.Div(
                                id="data-upload-dropdown-label-energy-prices",
                                children=[
                                    html.Div(
                                        className="upload__row",
                                        children=[
                                            html.Label("Energy Price Data"),
                                            dcc_date_picker(),
                                            upload_file("upload-energy-price-data")
                                        ]
                                    ),
                                ]
                            ),
                            html.Br(),
                            html.Div(
                                id="data-upload-dropdown-label-ess-data",
                                children=[
                                    html.Div(
                                        className="upload__row",
                                        children=[
                                            html.Label("ESS Data"),
                                            upload_file("upload-ess-data")
                                        ]
                                    ),
                                ]
                            ),
                            html.Br(),
                            ess_parameter_block(),
                        ]
                    ),
                    html.Br(),
                ]
            )
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
                                            className="usecase-switch",
                                            children=[
                                                html.Label("Control Type", className="usecase-dcr-label"),
                                                daq.BooleanSwitch(on=False, id="control-type-input1",
                                                                  className="usecase-switch-1", color="#007836",
                                                                  label="Optimization"),
                                                daq.BooleanSwitch(on=False, id="control-type-input2",
                                                                  className="usecase-switch-2", color="#cc3300",
                                                                  label="Rule-based"),

                                            ],

                                        ),
                                        # html.Button("Update", className="usecase-line-row", id="usecase-dcr-set-btn", n_clicks=0),
                                    ]

                                ),

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
                                            className="usecase-switch",
                                            children=[
                                                html.Label("Control Type", className="usecase-pfc-label"),
                                                daq.BooleanSwitch(on=False, id="control-type-input21",
                                                                  className="usecase-switch-1", color="#cc3300",
                                                                  label="Optimization"),
                                                daq.BooleanSwitch(on=False, id="control-type-input22",
                                                                  className="usecase-switch-2", color="#cc3300",
                                                                  label="Rule-based"),

                                            ],

                                        ),
                                    ]

                                ),

                                    # html.Button("Update", className="", id="usecase-pfc-set-btn", n_clicks=0),

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
        className="usecase-configuration__line",
        children=[
            html.Label(label, className="usecase-configuration__label"),
            daq.BooleanSwitch(on=False, className="usecase-configuration__switch", color="#00ab4d", id=switch_value),
            html.Div(
                dcc.Dropdown(
                    id=dd_value,
                    options=[
                        {'label': '1', 'value': 1},
                        {'label': '2', 'value': 2},
                        {'label': '3', 'value': 3},
                        {'label': '4', 'value': 4}
                    ],
                    disabled=True,
                ), className="usecase-configuration__dropdown",
            ),

            html.Button("Configure", className="usecase-configuration__set-button", id=value, disabled=True, n_clicks=0)
        ],

    )


def configuration_panel():
    """
    Function to get the system configuration panel
    """
    return html.Div(
        id="configuration-select-menu-wrapper",
        className="settings-container__configuration__wrapper",
        children=[
            html.Div(
                id="configuration-select-menu",
                className="settings-container__configuration",
                children=[
                    html.Div(
                        className="usecase-configuration",
                        children=[
                            html.H6("Use case Configuration"),
                            html.Br(),
                            # html.Br(),
                            html.Div(
                                id="usecase-header",
                                className="usecase-configuration__header",
                                children=[
                                    html.Label("Usecase",
                                               className="usecase-configuration__label"),
                                    html.Label("Select",
                                               className="usecase-configuration__switch"),
                                    html.Label("Priority",
                                               className="usecase-configuration__dropdown"),
                                    html.P("Configure Usecase", className="usecase-configuration__button-label"),
                                    # html.Div(col, className="value-setter")
                                ],
                            ),
                            build_usecase_line("demand-charge-reduction",
                                               "Demand Charge Reduction",
                                               "switch_dcr", "dd_dcr",
                                               "dcr"),
                            html.Br(),
                            build_usecase_line("power-factor-correction",
                                               "Power Factor Correction",
                                               "switch_pfc", "dd_pfc",
                                               "pfc"),
                            html.Br(),
                            build_usecase_line("arbitrage", "Arbitrage",
                                               "switch_arb", "dd_arb",
                                               "arb"),
                            html.Br(),
                            build_usecase_line("reserves-placement",
                                               "Reserves Placement",
                                               "switch_rp", "dd_rp",
                                               "rp"),
                            html.Br(),
                            html.Div(
                                id="dropdown-button",
                                className="usecase-configuration__button",
                                children=[html.Button(html.H6("Update"),
                                                      n_clicks=0)]
                            ), ]),

                ]
            ),

            # html.Br(),

            usecase_dcr_popup(),
            usecase_pfc_popup(),
        ]

    )


def build_ess_input_block(input_id, units, input_min, input_max, input_step, input_value):
    return html.Div(
        children=[
            html.Label(f"{input_id} ({units})", htmlFor="number"),
            dcc.Input(id="-".join(input_id.lower().split(" ")), type="number", min=input_min, max=input_max,
                      step=input_step, value=input_value)
        ],
        className="input-block__row"
    )


def build_all_ess_inputs():
    ess_data = [["Max SoC", "%", 50, 100, 10, 90], ["Min SOC", "%", 0, 50, 10, 10],
                ["Energy Capacity", "kWH", 100, 2000, 100, 1500], ["Max Power", "kW", 100, 1000, 50, 750]]
    inputs = []
    for data_set in ess_data:
        inputs.extend([build_ess_input_block(*data_set), html.Br()])
    return inputs


def ess_parameter_block():
    return html.Div(
        id="ess-parameter-block",
        className="upload__row input-block",
        children=[
            html.Label("ESS Parameters"),
            html.Br(),
            *build_all_ess_inputs()
        ])
