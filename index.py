import logging
import os

import dash
from dotenv import load_dotenv
from dash.dependencies import Input, Output, State
import LiveGraph

from app import app
from setting_layout import *
from simulation_layout import *
from network_layout import *

# add ability to access environment variables from .env, like os.environ.get(<VAR>)
load_dotenv()

ROUTES = [
    {
        'pathname': '/',
        'name': 'Configuration',
    },
    {
        'pathname': '/charts',
        'name': 'Viewer',
    },
    {
        'pathname': '/network',
        'name': 'Network',
    }
]

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("pyomo.core").setLevel(logging.INFO)
_log = logging.getLogger(__name__)
graph = LiveGraph.LiveGraph()

@app.callback(
    Output('graph-update', 'interval'),
    [Input('submit-rate', 'n_clicks')],
    [State('update-rate-box', 'value')]
)
def update_output(n_clicks, value):
    return value


@app.callback([Output("banner-button-config", "className"),
               Output("banner-button-dash", "className"),
               Output("banner-button-network", "className"),
               Output('settings-container', 'style'),
               Output('simulation-container', 'style'),
               Output('network-container', 'style')],
              [Input('url', 'pathname')])
def route(pathname):
    """
    builds the routes
    """
    class_name = "banner__button"

    classes = []
    styles = []
    for i, r in enumerate(ROUTES):
        possible_img_class = f' {class_name}--with-image' if i == 0 else ''
        if r['pathname'] == pathname:
            classes.append(f"{class_name}{possible_img_class}  {class_name}--active")
            styles.append(None)
        else:
            classes.append(class_name + possible_img_class)
            styles.append(dict(display="none"))

    return classes + styles


def build_navbar():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            dcc.Link(
                className='banner__button banner__button__with-image',
                id="banner-button-config",
                href='/',
                children=[
                    html.Img(id="logo", src=app.get_asset_url("pnnl_logo.svg"),
                             alt="Logo for Pacific Northwest "
                                 "National Laboratory"),
                    html.H4([ROUTES[0]['name'], html.I(className="fas fa-cog")]),
                ]
            ),
            dcc.Link(href='/charts', className='banner__button',
                     children=html.H4([ROUTES[1]['name'], html.I(className="fas fa-chart-line")]), id="banner-button-dash"),

            # For Network Tab
            dcc.Link(href='/network', className='banner__button',
                     children=html.H4([ROUTES[2]['name'], html.I(className="fas fa-project-diagram")]), id="banner-button-network"),

            html.Div(
                id="banner-text",
                className="banner__text",
                children=[
                    html.H4("Energy Storage Controls Learning and Evaluation (ESCLE)"),
                    #html.H5("Enhanced Control Dashboard"),
                ],
            )
        ],
    )


def serve_layout():
    return html.Div(
        className="app",
        children=[
            dcc.Location(id="url", refresh=False),
            build_navbar(),
            html.Div(
                id="big-app-container",
                className="main-content",
                children=[
                    html.Div(
                        id="app-container",
                        className="main-content",
                        children=[
                            dcc.Store(id="usecase-store", storage_type="session", data=LiveGraph.use_case_library),
                            dcc.Store(id="gen-config-store", storage_type="session", data=LiveGraph.gen_config),
                            dcc.Store(id="control-config-store", storage_type="session", data=LiveGraph.control_config),
                            dcc.Store(id="data-config-store", storage_type="session", data=LiveGraph.data_config),
                            dcc.Store(id="data-store", storage_type="session"),
                            dcc.Store(id="liveplot-store", storage_type="session"),
                            build_settings_tab(),
                            build_simulation_tab(),
                            build_network_tab(),
                            dcc.Interval(id='graph-update', interval=1000, max_intervals=1000, n_intervals=0,
                                         disabled=True),
                        ],
                    ),
                ],
            )])


app.layout = serve_layout


@app.callback(output=[Output(f"markdown{i + 1}", "style") for i in range(4)],
              inputs=[Input("dcr", "n_clicks"), Input("markdown-close1", "n_clicks"), Input("pfc", "n_clicks"),
                      Input("markdown-close2", "n_clicks"), Input("arb", "n_clicks"),
                      Input("markdown-close3", "n_clicks"), Input("rp", "n_clicks"),
                      Input("markdown-close4", "n_clicks")])
def open_modals(m1, c1, m2, c2, m3, c3, m4, c4):
    """
    opens/closes the modal elements
    """
    ctx = dash.callback_context
    inputs = list(ctx.inputs.keys())
    styles = [{"display": "none"} for _ in range(len(inputs) // 2)]

    if not ctx.triggered:
        return styles
    else:
        # get the index of the button that was clicked
        button_index = inputs.index(f"{ctx.triggered[0]['prop_id'].split('.')[0]}.n_clicks")

    # if the index of the button is even, show the corresponding modal element
    if button_index % 2 == 0:
        styles[button_index // 2] = {"display": "block"}
    return styles


@app.callback(
    output=[Output("dd_dcr", "disabled"), Output("dd_pfc", "disabled"), Output("dd_arb", "disabled"),
            Output("dd_rp", "disabled"), \
            Output("dcr", "disabled"), Output("pfc", "disabled"), Output("arb", "disabled"), Output("rp", "disabled")],
    inputs=[Input("switch_dcr", "on"), Input("switch_pfc", "on"), Output("switch_arb", "on"),
            Output("switch_rp", "on")],
)
def make_usecase_active(s1, s2, s3, s4):
    print(f"s1 = {s1}, s2 = {s2}, s3 = {s3}, s4 = {s4}")

    if s1:
        d1a, d1b = False, False
    else:
        d1a, d1b = True, True
    if s2:
        d2a, d2b = False, False
    else:
        d2a, d2b = True, True
    if s3:
        d3a, d3b = False, False
    else:
        d3a, d3b = True, True
    if s4:
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
    output=[Output("top-right-graph", "figure"), Output("top-left-graph", "figure"),
            Output("bottom-left-graph", "figure"),
            Output("bottom-right-graph", "figure"), Output("data-store", "data"), Output("liveplot-store", "data"),
            Output("revenue1", "value"),
            Output("revenue2", "value"), Output("revenue3", "value")],
    inputs=[Input("graph-update", "n_intervals"), Input("outage-switch", "value"), Input("external-switch", "value"),
            Input('stop-time', 'value')],
    state=[State('price-change-slider', 'value'), State('grid-load-change-slider', 'value'),
           State('update-window', 'value'), State('bottom-left-graph-dropdown', 'value'),
           State('bottom-right-graph-dropdown', 'value'),
           State('max-soc', 'value'), State('min-soc', 'value'), State('energy-capacity', 'value'),
           State('max-power', 'value'), State("data-store", "data"), State("liveplot-store", "data"),
           State("gen-config-store", "data"), State("usecase-store", "data")])
# @cache.memoize
def update_graph(n_intervals, has_outage, is_external, fig_stop_time, price_value,
               grid_load_value, update_window_rate, left_dropdown_value, right_dropdown_value, max_soc, min_soc,
               energy_capacity, max_power, data_store, live_data_store, config_store, use_case_store):
    return graph.update(n_intervals, has_outage, is_external, fig_stop_time, price_value,
                       grid_load_value, update_window_rate, left_dropdown_value, right_dropdown_value, max_soc, min_soc,
                       energy_capacity, max_power, data_store, live_data_store, config_store, use_case_store)

if __name__ == '__main__':
    truthy_values = ('true', '1')
    should_debug = os.environ.get('DEBUG').lower() in truthy_values
    _log.debug("Creating server now.")
    app.run_server(debug=should_debug, port=os.environ.get('PORT'))
