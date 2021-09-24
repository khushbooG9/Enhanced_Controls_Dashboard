from configuration import (
    use_case_library,
    gen_config,
    control_config,
    data_config,
    battery_obj
)
from collections import deque
from datetime import timedelta
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

CHART_BACKGROUND_COLOR = '#616265'
CHART_HEIGHT = 450
CHART_WIDTH = 700
UPDATE_BUFFER = 3600 * 24
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
NEW_RESERVE_UP_CAP = 500  # kW/5 minutes
NEW_RESERVE_DOWN_CAP = 500  # kW/5 minutes


# changes variables in a given config store
def update_config_store(config_store, max_power, min_soc):
    config_store['rated_kW'] = max_power
    config_store['reserve_soc'] = min_soc / 100


# gets the data range from the config store, as datetime objects
def get_date_range(config_store):
    start_time = config_store['StartTime']
    start_time = datetime.strptime(start_time, TIME_FORMAT)
    end_time = config_store['EndTime']
    end_time = datetime.strptime(end_time, TIME_FORMAT)
    return start_time, end_time


class LiveGraph:
    def __init__(self):
        self.battery = battery_obj
        self.use_case_data = use_case_library
        self.config_data = gen_config
        self.control_data = control_config
        self.data_config = data_config

    def create_graph(self, n_intervals, prediction_data, actual_data, max_soc, min_soc, start_time,
                     fig_stop_time, update_window_rate, title=None, **kwargs):
        dict_fig = {'linewidth': 2, 'linecolor': CHART_BACKGROUND_COLOR, 'width': CHART_WIDTH, 'height': CHART_HEIGHT,
                    'xaxis_title': 'Seconds', 'yaxis_title': 'kW'}
        margin_constant = 0.15
        if kwargs:
            dict_fig.update(kwargs)
        legend_dict = dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[i * 3600 for i in range(0, len(prediction_data))],
            y=prediction_data,
            name="Prediction"))
        fig.add_trace(go.Scatter(
            x=[i for i in range(max(0, n_intervals - UPDATE_BUFFER), (n_intervals + 1))],
            y=[i for i in deque(actual_data, maxlen=UPDATE_BUFFER)],
            name="Actual"))

        if title == "SoC":
            fig.add_shape(type="line", x0=-2, y0=max_soc, x1=n_intervals + 4, y1=max_soc,
                          line=dict(color="LightSeaGreen", dash="dashdot"))
            fig.add_shape(type="line", x0=-2, y0=min_soc, x1=n_intervals + 4, y1=min_soc,
                          line=dict(color="MediumPurple", dash="dashdot"))

        start_interval_figure = max(0, n_intervals - update_window_rate)
        stop_interval_figure = max(n_intervals, fig_stop_time)

        ymin, ymax = min([prediction_data[0]] + actual_data[start_interval_figure:n_intervals]), max(
            [prediction_data[0]] + actual_data[start_interval_figure:n_intervals])

        if ymin <= 1:
            margin_constant = 0.05

        min_margin = abs(ymin * margin_constant)
        max_margin = abs(ymax * margin_constant)

        fig.update_xaxes(range=[start_interval_figure, stop_interval_figure], showline=True, linewidth=2,
                         linecolor='#e67300', mirror=True)

        if title == "SoC":
            ymin, ymax = 0, 100
        else:
            ymin, ymax = ymin - min_margin, ymax + max_margin

        fig.add_annotation(x=start_interval_figure, y=ymin,
                           text=str((start_time + timedelta(seconds=start_interval_figure)).time()),
                           showarrow=False,
                           yshift=-50)
        fig.add_annotation(x=start_interval_figure, y=ymin,
                           text=str((start_time + timedelta(seconds=stop_interval_figure)).time()),
                           showarrow=False,
                           yshift=-50,
                           xshift=550)

        fig.update_yaxes(range=[ymin, ymax], showline=True, linewidth=2, linecolor='#e67300', mirror=True)
        # fig.update_yaxes(showline=True, linewidth=2, linecolor='#e67300', mirror=True)
        fig.update_layout(paper_bgcolor=dict_fig['linecolor'], width=dict_fig['width'], height=dict_fig['height'],
                          legend=legend_dict, showlegend=True, title=title,
                          xaxis_title=dict_fig['xaxis_title'],
                          yaxis_title=dict_fig['yaxis_title'], font_color="rgba(245, 245, 245, 0.6)")
        return fig

    # updates the charts
    def update(self, n_intervals, has_outage, is_external, fig_stop_time, price_value,
               grid_load_value, update_window_rate, left_dropdown_value, right_dropdown_value, max_soc, min_soc,
               energy_capacity, max_power, data_store, live_data_store, config_store, use_case_store):
        start_time, end_time = get_date_range(config_store)
        update_config_store(config_store, max_power, min_soc)

        data = {}
        new_battery_setpoint = 0.0
        new_grid_load = 0.0
        new_grid_reactive_power = 0.0
        new_SoC = 0.0
        new_battery_reactive_power = 0.0
        simulation_duration, current_time, SoC_temp, services_list, priority_list = None, None, None, None, None

        if n_intervals == 0:
            simulation_duration = int((end_time - start_time).total_seconds())
            current_time = start_time

            services_list = list(use_case_store.keys())
            priority_list = []
            for key, value in use_case_store.items():
                priority_list.append(use_case_store[key]["priority"])
            SoC_temp = self.battery.SoC_init
        elif n_intervals > 0:
            self.battery.fromdict(live_data_store)
            simulation_duration = data_store["simulation_duration"]
            current_time = datetime.strptime(data_store["current_time"], "%Y-%m-%d %H:%M:%S")
            services_list = data_store["services_list"]
            priority_list = data_store["priority_list"]
            SoC_temp = data_store["SoC_temp"]

        new_actual_load = battery_obj.actual_load[-1] if len(battery_obj.actual_load) else -1
        if n_intervals < simulation_duration:
            if n_intervals % 3600 == 0:
                battery_obj.set_hourly_load_forecast(current_time, current_time + timedelta(days=1))
                # print("just before price forecast")
                battery_obj.set_hourly_price_forecast(current_time, current_time + timedelta(days=1), n_intervals)
                battery_obj.DA_optimal_quantities()

            battery_obj.set_load_actual(battery_obj.load_predict[0],
                                        np.mean(np.diff(battery_obj.load_predict[0:3])) * battery_obj.hrs_to_secs)

            # if (n_intervals % 300 == 0):
            battery_obj.set_price_actual(battery_obj.price_predict[0],
                                         (battery_obj.price_predict[1] - battery_obj.price_predict[
                                             0]) * 300 * battery_obj.hrs_to_secs, n_intervals)

            # change price and load values given there is a user input to change it
            new_actual_price = max(0.0001,
                                   battery_obj.actual_price[-1] + battery_obj.actual_price[
                                       -1] * price_value / 100)
            new_actual_load = max(0, battery_obj.actual_load[-1] + battery_obj.actual_load[-1] * (
                    grid_load_value / 100))

            current_reg_signal = battery_obj.get_reg_signal(current_time, n_intervals)
            print(f"current reg signal = {current_reg_signal}")
            if has_outage:
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
                    service_priority = services_list[i + 1]
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
                                    battery_obj.grid_react_power_prediction[0] +
                                    battery_obj.battery_react_power_prediction[
                                        0]))

                            new_battery_reactive_power = battery_obj.battery_react_power_prediction[
                                                             0] - battery_ratio * reactive_power_mismatch
                            new_grid_reactive_power = battery_obj.load_pf * new_grid_load + new_battery_reactive_power

                if is_external:
                    if NEW_RESERVE_DOWN_CAP < 0.0:
                        new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                                                                           current_reg_signal * NEW_RESERVE_DOWN_CAP * (
                                                                                   1 / (5 * 60)))
                        new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, SoC_temp)

                    elif NEW_RESERVE_DOWN_CAP > 0.0:
                        new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                                                                           current_reg_signal * NEW_RESERVE_UP_CAP * (
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
        battery_obj.peak_load_actual.append(max(battery_obj.grid_load_actual[0:n_intervals + 1]))
        SoC_temp = new_SoC
        ln = len(battery_obj.peak_load_actual)
        current_time = current_time + timedelta(seconds=+1)
        fig_dict = {}
        fig_pf_dict = {'yaxis_title': '-'}
        fig_price_dict = {'yaxis_title': '$/kWh'}
        fig_reactive_dict = {'yaxis_title': 'kVAR'}
        fig_soc_dict = {'yaxis_title': '%'}
        fig1 = self.create_graph(ln, [x * (100 / battery_obj.rated_kWh) for x in battery_obj.SoC_prediction],
                                 [y * (100 / battery_obj.rated_kWh) for y in battery_obj.SoC_actual], max_soc,
                                 min_soc, start_time, fig_stop_time, update_window_rate,
                                 "SoC", **fig_soc_dict)

        fig2 = self.create_graph(ln, battery_obj.battery_setpoints_prediction,
                                 battery_obj.battery_setpoints_actual, max_soc, min_soc, start_time,
                                 fig_stop_time, update_window_rate,
                                 "Battery Setpoint", **fig_dict)

        # print(f"price predict = {battery_obj.price_predict}")
        peak_load_prediction = [battery_obj.peak_load_prediction] * 24

        fig_obj = {"PL": [peak_load_prediction, battery_obj.peak_load_actual, fig_dict],
                   "GR": [battery_obj.grid_react_power_prediction, battery_obj.grid_react_power_actual,
                          fig_reactive_dict],
                   "BR": [battery_obj.battery_react_power_prediction, battery_obj.battery_react_power_actual,
                          fig_reactive_dict],
                   "GI": [battery_obj.grid_load_prediction, battery_obj.grid_load_actual, fig_dict],
                   "EP": [battery_obj.price_predict, battery_obj.actual_price, fig_price_dict],
                   "PF": [battery_obj.grid_power_factor_prediction, battery_obj.grid_power_factor_actual,
                          fig_pf_dict],
                   "D": [battery_obj.load_up, battery_obj.grid_load_actual,
                          fig_pf_dict]
                   }

        fig3 = self.create_graph(ln, fig_obj[left_dropdown_value][0], fig_obj[left_dropdown_value][1], max_soc,
                                 min_soc, start_time, fig_stop_time, update_window_rate,
                                 **fig_obj[left_dropdown_value][2])
        fig4 = self.create_graph(ln, fig_obj[right_dropdown_value][0], fig_obj[right_dropdown_value][1], max_soc,
                                 min_soc, start_time, fig_stop_time, update_window_rate,
                                 **fig_obj[right_dropdown_value][2])

        data["SoC_temp"] = SoC_temp
        data["simulation_duration"] = simulation_duration
        data["services_list"] = services_list
        data["priority_list"] = priority_list
        data["current_time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        # calculating Revenue

        battery_obj.metrics['peak_surcharge_da'].append(battery_obj.peak_load_prediction * battery_obj.peak_price)
        battery_obj.metrics['original_surcharge'].append(max(battery_obj.peak_load_actual) * battery_obj.peak_price)
        print(f"battery_obj.load_up = {battery_obj.load_up}")
        print(f"new_actual_load = {new_actual_load}")
        print(f"peak price = {battery_obj.peak_price}")
        nonoptimized_surcharge = max(battery_obj.load_up)*battery_obj.peak_price
        noncorrected_surcharge = max(max(battery_obj.load_up),new_actual_load)*battery_obj.peak_price # check whether this is the actual load in real-time when not corrected
        # print('da surcharge' + str(battery_obj.metrics['peak_surcharge_da'][-1]))
        # print('real time surcharge' + str(battery_obj.metrics['original_surcharge'][-1]))
        revenue1 = round(nonoptimized_surcharge-battery_obj.metrics['peak_surcharge_da'][-1], 2)# estimated savings
        revenue2 = round(noncorrected_surcharge-battery_obj.metrics['peak_surcharge_da'][-1], 2)# estimated actual savings, but when no correction is done
        revenue3 = round(battery_obj.metrics['peak_surcharge_da'][-1]-battery_obj.metrics['original_surcharge'][-1], 2)# estimated actual savings, with correction

        battery_dict = battery_obj.todict()
        print('at the end', gen_config['rated_kW'])

        return [fig1, fig2, fig3, fig4, data, battery_dict, revenue1, revenue2, revenue3]
