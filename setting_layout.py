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
                      children=[html.I(className="fas fa-upload"), html.Label(" Drag and drop or select a file",
                                                                              htmlFor="file")], className="upload__file"
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
                            upload_model_block(),
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


def build_popup(container_id, background_id, close_button_id, switch1_id, switch2_id, numeric_input_data):
    """
    creates a popup for use case configuration, which is by default hidden
    Args:
        container_id (str): id for the whole element
        background_id (str): id for background container
        close_button_id (str): id for the button to close the modal
        switch1_id (str): id for the first switch
        switch2_id (str): id for the second switch
        numeric_input_data (list<tuple>): lists of data to create numeric inputs

    """
    return html.Div(
        id=container_id,
        style={"display": "none"},
        className="modal",
        children=(
            html.Div(
                id=background_id,
                className="modal__container",
                children=(
                    html.Div(
                        className="modal__close-container",
                        children=html.Button(
                            [html.P("Close"), html.I(className="far fa-times-circle")],
                            id=close_button_id,
                            n_clicks=0,
                            className="modal__close-button",
                        ),
                    ),

                    html.Div(
                        className="modal__content",
                        children=(

                            html.H6("Configuration"),
                            html.Div(

                                className="modal__header",

                                children=[
                                    html.Label("Setting Name", className="modal__label"),
                                    # html.Label("Setting Name", className="usecase-pfc-label"),
                                    html.Label("Setting Input", className="modal__input")
                                    # html.Label("Setting Input", className="usecase-setting-input")
                                ],
                            ),
                            *[html.Div(
                                id=data[0],
                                className="modal__row modal__row--margin-bottom" if i == len(numeric_input_data) - 1
                                else "modal__row",

                                children=(
                                    html.Label(data[1], className="modal__label"),
                                    daq.NumericInput(id=f"{data[0]}-input", className="modal__input", size=110,
                                                     min=data[2], max=data[3], value=data[4])
                                )
                            ) for i, data in enumerate(numeric_input_data)],

                            html.Br(),
                            html.Div(
                                className="modal__switches",
                                children=[
                                    html.Label("Control Type", className="modal__label"),
                                    # html.Label("Control Type", className="usecase-pfc-label"),
                                    daq.BooleanSwitch(on=False, id=switch1_id,
                                                      className="modal__switches__switcher", color="#007836",

                                                      label="Optimization"),
                                    daq.BooleanSwitch(on=False, id=switch2_id,
                                                      className="modal__switches__switcher", color="#007836",

                                                      label="Rule-based"),

                                ],

                            ),
                        )
                    )
                )
            )
        ))


def build_usecase_line(line_num, label, switch_value, dd_value, value):
    return html.Div(
        id=line_num,
        className="usecase-configuration__line",
        children=[
            html.Label(label, className="usecase-configuration__label"),
            daq.BooleanSwitch(on=False, className="usecase-configuration__switch", color="#007836", id=switch_value),
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
    # [(input_id, label, min, max, value), ...]
    dcr_numeric_input_data = [("peak-charge", "Peak Charge", 0, 1000, 5), ("threshold", "Threshold", 0, 1000, 5),
                              ("uncertainty-budget", "Uncertainty Budget", 0, 1000, 5)]
    pfc_numeric_input_data = [("load-power-factor", "Load Power Factor", 0, 1000, 5), ("power-factor-limit",
                                                                                       "Power Factor Limit", 0, 1000,
                                                                                       5)]
    # todo create meaningful input data for the arbitrage and reserves placement modals
    arbitrage_numeric_input_data = [("arb1", "Load Power Factor", 0, 1000, 5), ("arb2", "Power Factor Limit", 0, 1000,
                                                                                5)]
    res_placement_numeric_input_data = [("resp1", "Load Power Factor", 0, 1000, 5), ("resp2", "Power Factor Limit", 0,
                                                                                     1000, 5)]
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

            # modal popups for configuring the use cases
            build_popup("markdown1", "markdown-container1", "markdown-close1", "modal1-control-type1",
                        "modal1-control-type2", dcr_numeric_input_data),
            build_popup("markdown2", "markdown-container2", "markdown-close2", "modal2-control-type1",
                        "modal2-control-type2", pfc_numeric_input_data),
            build_popup("markdown3", "markdown-container3", "markdown-close3", "modal3-control-type1",
                        "modal3-control-type2", arbitrage_numeric_input_data),
            build_popup("markdown4", "markdown-container4", "markdown-close4", "modal4-control-type1",
                        "modal4-control-type2", res_placement_numeric_input_data),
        ]

    )


def build_ess_input_block(input_id, units, input_min, input_max, input_step, input_value):
    return html.Div(
        children=[
            html.Label(f"{input_id} ({units})", htmlFor="number", className="input-block__input-label"),
            dcc.Input(id="-".join(input_id.lower().split(" ")), type="number", min=input_min, max=input_max,
                      step=input_step, value=input_value, className="input-block__input")
        ],
        className="input-block__row"
    )


def build_all_ess_inputs():
    ess_data = [["Max SoC", "%", 50, 100, 10, 90], ["Min SOC", "%", 0, 50, 10, 10],
                ["Energy Capacity", "kWH", 100, 2000, 100, 1500], ["Max Power", "kW", 100, 1000, 50, 750]]
    inputs = []
    for i, data_set in enumerate(ess_data):
        new_inputs = [build_ess_input_block(*data_set)]
        # add a break after all but the last data set
        if i < len(ess_data) - 1:
            new_inputs.append(html.Br())
        inputs.extend(new_inputs)
    return html.Div(inputs, className="input-block__rows")


def ess_parameter_block():
    return html.Div(
        id="ess-parameter-block",
        className="upload__row input-block",
        children=[
            html.Label("ESS Parameters", className="input-block__title"),
            html.Br(),
            build_all_ess_inputs()
        ])


def upload_model_block():
    return html.Div(
        id="upload-model-block",
        className="upload__row",
        children=[
            html.Label("Upload Model"),
            dcc_date_picker(),
            upload_file("upload-model-data")
        ]
    )
