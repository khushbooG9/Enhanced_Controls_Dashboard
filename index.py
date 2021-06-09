from app import *
from setting_layout import *
from simulation_layout import *
import dash
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
from collections import deque
import json
import jsonpickle
from json import JSONEncoder
from plotly.subplots import make_subplots

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
    return html.Div([
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
        [
        html.Div(
        id="big-app-container",
        children=[
            build_banner(),
            html.Div(
                id="app-container",
                children=[
                    dcc.Store(id="usecase-store", storage_type="session", data=init_usecase()),
                    dcc.Store(id="gen-config-store", storage_type="session", data=init_gen_config()),
                    dcc.Store(id="control-config-store", storage_type="session", data=init_control_config()),
                    dcc.Store(id="data-config-store", storage_type="session", data=init_data_config()),
                    dcc.Store(id="data-store", storage_type="session"),
                    dcc.Store(id="liveplot-store", storage_type="session"),
                    build_tabs(),
                    html.Div(id="app-content")
                ],
            ),
        ],
    )])

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
    output=[Output("right-graph-fig", "figure"), Output("left-graph-fig", "figure"), Output("down-left-graph", "figure"),
            Output("down-right-graph", "figure"), Output("data-store", "data"), Output("liveplot-store", "data"), Output("revenue1", "value"),
            Output("revenue2", "value"), Output("revenue3", "value")],
    inputs=[Input("graph-update", "n_intervals"), Input("outage-switch", "value"),  Input("external-switch", "value"), Input("submit-val", "n_clicks"),
            Input('start-time', 'value')],
    state=[State('price-change-slider', 'value'), State('grid-load-change-slider', 'value'),
           State('update-window', 'value'), State('fig-left-dropdown', 'value'), State('fig-right-dropdown', 'value'),
           State('max-soc', 'value'), State('min-soc', 'value'), State('energy-capacity', 'value'),
           State('max-power', 'value'), State("data-store", "data"), State("liveplot-store", "data"),
           State("gen-config-store", "data"), State("data-config-store", "data"), State("usecase-store", "data")])
# @cache.memoize
# fig1= None


def update_live_graph(ts, outage_flag, external_signal_flag, submit_click, fig_start_time, price_change_value, grid_load_change_value, update_window,
                      fig_leftdropdown, fig_rightdropdown, ess_soc_max_limit, ess_soc_min_limit, ess_capacity, max_power,  data1, live1,
                      gen_config, data_config,
                      use_case_library):

    update_buffer = 3600*24
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
        # fig.add_trace(go.Scatter(
        #     x=[i for i in range(max(0, ts - update_buffer), (ts + 1))],
        #     y=[i for i in deque(prediction_data, maxlen=update_buffer)],
        #     name="Prediction"))
        fig.add_trace(go.Scatter(
            x=[i for i in range(max(0, ts - update_buffer), (ts + 1))],
            y=[i for i in deque(actual_data, maxlen=update_buffer)],
            name="Actual"))

        if title == "SoC":
            fig.add_shape(type="line", x0=-2, y0=ess_soc_max_limit, x1=ts+4, y1=ess_soc_max_limit,
                          line=dict(color="LightSeaGreen", dash="dashdot"))
            fig.add_shape(type="line", x0=-2, y0=ess_soc_min_limit, x1=ts + 4, y1=ess_soc_min_limit,
                          line=dict(color="MediumPurple", dash="dashdot"))
        ymin, ymax = min([prediction_data[0]] + actual_data[max(fig_start_time, ts - update_window):ts]), max([prediction_data[0]] + actual_data)
        min_margin = abs(ymin * 0.1)
        max_margin = abs(ymin * 0.1)

        fig.update_xaxes(range=[max(fig_start_time, ts - update_window), ts], showline=True, linewidth=2, linecolor='#e67300',
                         mirror=True)
        if title == "SoC":
            ymin, ymax = 0, 100
        else:
            ymin, ymax = ymin - min_margin, ymax + max_margin

        # fig.add_annotation(x=max(fig_start_time, ts - update_window), y=ymin,
        #                    text="Start Time",
        #                    showarrow=False,
        #                    yshift=-50)
        # fig.add_annotation(x=max(fig_start_time, ts - update_window), y=ymin,
        #                    text="Stop Time",
        #                    showarrow=False,
        #                    yshift=-50,
        #                    xshift= 450)

        fig.update_yaxes(range=[ymin, ymax], showline=True, linewidth=2, linecolor='#e67300', mirror=True)
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
    # gen_config['bat_capacity_kWh'] = ess_capacity
    gen_config['rated_kW'] = max_power
    gen_config['reserve_soc'] = ess_soc_min_limit / 100
    battery_obj = battery_class_new(use_case_library, gen_config, data_config)
    new_reserve_up_cap = 500  # kW/5 minutes
    new_reserve_down_cap = 500  # kW/5 minutes

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
            #print("just before price forecast")
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
        #print(f"price predict = {battery_obj.price_predict[0]}")
        battery_obj.set_load_actual(battery_obj.load_predict[0], np.mean(np.diff(battery_obj.load_predict[0:3])) * battery_obj.hrs_to_secs )

        # if (ts % 300 == 0):
        battery_obj.set_price_actual(battery_obj.price_predict[0],
                                     (battery_obj.price_predict[1] - battery_obj.price_predict[0]) * 300 * battery_obj.hrs_to_secs, ts)

        # change price and load values given there is a user input to change it
        new_actual_price = max(0.0001, battery_obj.actual_price[-1] + battery_obj.actual_price[-1] * price_change_value / 100)
        new_actual_load = max(0, battery_obj.actual_load[-1] + battery_obj.actual_load[-1] * (
                    grid_load_change_value / 100))

        current_reg_signal = battery_obj.get_reg_signal(current_time, ts)
        print(f"current reg signal = {current_reg_signal}")
        if outage_flag:
            check = 1
            # outage mitigation
            active_power_mismatch = new_actual_load
            new_battery_setpoint = battery_obj.change_setpoint(0, active_power_mismatch)
            new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, SoC_temp)
            new_grid_load = new_actual_load - new_battery_setpoint
            reactive_power_mismatch = battery_obj.load_pf * active_power_mismatch
            new_battery_reactive_power = -reactive_power_mismatch
            new_grid_reactive_power = 0.0

        else:
            active_power_mismatch = new_actual_load
            new_grid_load = new_actual_load - new_battery_setpoint
            reactive_power_mismatch = battery_obj.load_pf * active_power_mismatch
            new_battery_reactive_power = -reactive_power_mismatch
            new_grid_reactive_power = 0.0
            active_power_mismatch = new_actual_load - battery_obj.load_up[0]
            reactive_power_mismatch = battery_obj.load_pf * active_power_mismatch
            for i in range(len(services_list) - 1):
                service_priority = services_list[priority_list.index(i + 1)]
                if service_priority == "demand_charge":
                    # check demand charge reduction in real-time
                    new_SoC, new_battery_setpoint, new_grid_load = battery_obj.rtc_demand_charge_reduction \
                        (i, active_power_mismatch, battery_obj.battery_setpoints_prediction[0], SoC_temp,
                         new_actual_load)

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

            if external_signal_flag:
                if new_reserve_down_cap < 0.0:
                    new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                                                                       current_reg_signal * new_reserve_down_cap * (
                                                                                   1 / (5 * 60)))
                    new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, SoC_temp)

                elif new_reserve_down_cap > 0.0:
                    new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                                                                       current_reg_signal * new_reserve_up_cap * (
                                                                                   1 / (5 * 60)))
                    new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, SoC_temp)

    battery_obj.SoC_actual.append(SoC_temp)
    battery_obj.battery_setpoints_actual.append(new_battery_setpoint)
    battery_obj.grid_load_actual.append(new_grid_load)
    battery_obj.battery_react_power_actual.append(new_battery_reactive_power)
    battery_obj.actual_load.append(new_actual_load)

    # battery_obj.grid_react_power_actual.append(battery_obj.load_pf * new_grid_load + new_battery_reactive_power)

    battery_obj.grid_react_power_actual.append(new_grid_reactive_power)
    new_grid_apparent_power = battery_obj.get_apparent_power(new_grid_load, new_grid_reactive_power)
    battery_obj.grid_apparent_power_actual.append(new_grid_apparent_power)
    new_power_factor = battery_obj.get_power_factor(new_grid_load, new_grid_apparent_power)
    battery_obj.grid_power_factor_actual.append(new_power_factor)
    battery_obj.peak_load_actual.append(max(battery_obj.grid_load_actual[0:ts+1]))
    SoC_temp = new_SoC
    battery_obj.metrics['peak_surcharge_da'].append(battery_obj.peak_load_prediction * battery_obj.peak_price)
    battery_obj.metrics['original_surcharge'].append(max(battery_obj.peak_load_actual) * battery_obj.peak_price)

    # print('da surcharge' + str(battery_obj.metrics['peak_surcharge_da'][-1]))
    # print('real time surcharge' + str(battery_obj.metrics['original_surcharge'][-1]))
    ln = len(battery_obj.peak_load_actual)
    current_time = current_time + timedelta(seconds=+1)
    fig_dict = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                'xaxis_title': 'Seconds', 'yaxis_title': 'kW'}
    fig_pf_dict = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                'xaxis_title': 'Seconds', 'yaxis_title': '-'}
    fig_price_dict = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                'xaxis_title': 'Seconds', 'yaxis_title': '$/kWh'}
    fig_reactive_dict = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                'xaxis_title': 'Seconds', 'yaxis_title': 'kVAR'}
    fig_soc_dict = {'linewidth': 2, 'linecolor': '#EFEDED', 'width': 600, 'height': 400,
                    'xaxis_title': 'Seconds', 'yaxis_title': '%'}
    fig1 = dash_fig(ln, [x * (100/ battery_obj.rated_kWh) for x in battery_obj.SoC_prediction],
                    [y * (100/ battery_obj.rated_kWh) for y in battery_obj.SoC_actual],
                    "SoC", **fig_soc_dict)

    fig2 = dash_fig(ln, battery_obj.battery_setpoints_prediction,
                    battery_obj.battery_setpoints_actual,
                    "Battery Setpoint", **fig_dict)

    print(f"price predict = {battery_obj.price_predict}")
    peak_load_prediction = [battery_obj.peak_load_prediction] * 24 * 3600
    def list_conversion (a):
        return [j for i in [[x]*3600 for x in a] for j in i]

    fig_obj = {"PL": [peak_load_prediction, battery_obj.peak_load_actual, fig_dict],
               "GR": [battery_obj.grid_react_power_prediction, battery_obj.grid_react_power_actual, fig_reactive_dict],
               "BR": [battery_obj.battery_react_power_prediction, battery_obj.battery_react_power_actual, fig_reactive_dict],
               "GI": [battery_obj.grid_load_prediction, battery_obj.grid_load_actual, fig_dict],
               "EP": [battery_obj.price_predict, battery_obj.actual_price, fig_price_dict],
               "PF": [battery_obj.grid_power_factor_prediction, battery_obj.grid_power_factor_actual, fig_pf_dict]}


    fig3 = dash_fig(ln, fig_obj[fig_leftdropdown][0], fig_obj[fig_leftdropdown][1], **fig_obj[fig_leftdropdown][2])
    fig4 = dash_fig(ln, fig_obj[fig_rightdropdown][0], fig_obj[fig_rightdropdown][1], **fig_obj[fig_rightdropdown][2])

    data["SoC_temp"] = SoC_temp
    data["simulation_duration"] = simulation_duration
    data["services_list"] = services_list
    data["priority_list"] = priority_list
    data["current_time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    revenue1 = round(battery_obj.metrics['peak_surcharge_da'][-1], 2)
    revenue2 = revenue1
    revenue3 = round(battery_obj.metrics['original_surcharge'][-1], 2)

    live = battery_obj.todict()

    return [fig1, fig2, fig3, fig4, data, live, revenue1, revenue2, revenue3]


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
