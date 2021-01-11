import os
import sys
import json
import numpy as np
from datetime import datetime, timedelta

from battery_class_new import battery_class_new
import matplotlib.animation as ani
import matplotlib.pyplot as plt
import logging


def construct_use_case_library(gen_config, control_config):


    with open("use_case_library_skeleton.json", 'r', encoding='utf-8') as lp:
        use_case_config = json.load(lp)

    for key, value in control_config.items():
        use_case_config[key]["priority"] = control_config[key]["priority"]

        if key == "power_factor_correction":
            use_case_config[key]["power_factor_limit"] = gen_config["pf_limit"]
            use_case_config[key]["power_factor_penalty"] = gen_config["pf_penalty"]
            if control_config[key]["optimization_based"] == 1:
                use_case_config[key]["control_type"] = "opti-based"
                use_case_config[key]["linearization_segments"] = gen_config["linearization_segments"]
            else:
                use_case_config[key]["control_type"] = "rule-based"

        if key == "demand_charge":
            use_case_config[key]["peak_price"] = gen_config["peak_price"]
            use_case_config[key]["peak_threshold"] = gen_config["peak_threshold"]
            use_case_config[key]["peak_price"] = gen_config["peak_price"]
            if control_config[key]["optimization_based"] == 1:
                use_case_config[key]["control_type"] = 'opti-based'
                use_case_config[key]["budget_uncertainty"] = gen_config["demand_charge_budget"]
            else:
                use_case_config[key]["control_type"] = 'rule-based'


        if key == "energy_arbitrage":
            if control_config[key]["optimization_based"] == 1:
                use_case_config[key]["control_type"] = 'opti-based'
                use_case_config[key]["budget_uncertainty"] = gen_config["arbitrage_budget"]
            else:
                use_case_config[key]["control_type"] = 'rule-based'
                use_case_config[key]["arbitrage_price_threshold"] = gen_config["arbitrage_price_threshold"]


        if key == "reserves_placement":
            if control_config[key]["optimization_based"] == 1:
                use_case_config[key]["control_type"] = 'opti-based'
                use_case_config[key]["max_reserve_up_cap"] = gen_config["max_reserve_up_cap"]
                use_case_config[key]["max_reserve_down_cap"] = gen_config["max_reserve_down_cap"]
            else:
                use_case_config[key]["control_type"] = 'rule-based'
                use_case_config[key]["max_reserve_up_cap"] = gen_config["max_reserve_up_cap"]
                use_case_config[key]["max_reserve_down_cap"] = gen_config["max_reserve_down_cap"]

    if key == "external_signal":
        if control_config[key]["applied"] == 1:
            use_case_config[key]["enabled"] = "yes"
        else:
            use_case_config[key]["enabled"] = "no"

    return use_case_config

def store_dict_to_json(ts, variables, id):
    with open("results_data\\" + str(ts) + '_' + id + '.json', 'w') as fp:
        json.dump(variables, fp)


def clean_dict(dict, id):
    if id == "da":
        dict = {'Time': [], 'battery_setpoints_da': [], 'SoC_da': [], 'grid_load_da': [], 'peak_load_da': [],
                        'react_grid_da': [], 'react_batt_da': [], 'grid_pf_da': [], 'total_load_predict_da': [],
                        'price_predict_da': [], 'arbitrage_purchased_power_da': [], 'reg_up_cap_da': [],
                        'reg_down_cap_da': [], 'reg_price_predict_up': [], 'reg_price_predict_down': []}

    elif id == "rt":
        dict = {'Time': [], 'battery_setpoints_rt': [], 'SoC_rt': [], 'grid_load_rt': [], 'peak_load_rt': [],
                        'react_grid_rt': [], 'react_batt_rt': [], 'grid_pf_rt': [], 'total_load_actual_rt': [],
                        'price_actual_rt': [], 'arbitrage_purchased_power_ideal_rt': [],
                        'arbitrage_purchased_power_actual_rt': [],
                        'reg_price_up_rt': [], 'reg_price_down_rt': [], 'reg_up_cap_rt': [], 'reg_down_cap_rt': []}
    elif id == 'results':
        dict = {'Time': [], 'arbitrage_revenue_da': [], 'peak_surcharge_da': [], 'arbitrage_revenue_ideal_rt': [], 'arbitrage_revenue_actual_rt': [], 'peak_surcharge_rt': [], 'original_surcharge': [],
               'reg_up_rev_da': [], 'reg_down_rev_da': [], 'reg_up_rev_rt': [], 'reg_down_rev_rt': []}

    return dict


if __name__ == "__main__":

    pre_file = 'results_data\\'
    with open("dict.json", 'r', encoding='utf-8') as lp:
        gen_config = json.load(lp)

    with open("control_fields.json", 'r', encoding='utf-8') as lp:
        control_config = json.load(lp)

    with open("data_paths.json", 'r', encoding='utf-8') as lp:
        data_config = json.load(lp)

    time_format = '%Y-%m-%d %H:%M:%S'
    start_time = gen_config['StartTime']
    end_time = gen_config['EndTime']
    simulation_duration = int((datetime.strptime(end_time, time_format) -
                               datetime.strptime(start_time, time_format)).total_seconds())+1
    current_time = datetime.strptime(start_time, time_format)

    print('simulation start time -> ' + start_time)
    print('simulation end time -> ' + end_time)
    print('simulation duration in seconds -> ' + str(simulation_duration))

    use_case_library = construct_use_case_library(gen_config, control_config)

    print("Use Cases Loaded")


    services_list = list(use_case_library.keys())
    priority_list = []
    for key, value in use_case_library.items():
        priority_list.append(use_case_library[key]["priority"])

    battery_obj = battery_class_new(use_case_library, gen_config, data_config)

    print("Battery Object Loaded")

    battery_obj.get_data()
    ts = 0
    new_SoC = battery_obj.SoC_init
    # new_SoC = SoC_temp
    new_battery_setpoint = 0.0
    new_reserve_up_cap = 0.0
    new_reserve_down_cap = 0.0
    batt_temp = 0.0
    load_temp = 0.0
    load_react_temp = 0.0
    grid_act_power_temp = 0.0
    grid_react_power_temp = 0.0
    batt_react_power_temp = 0.0
    battery_react_power_ratio = 0.0
    grid_react_power_ratio = 0.0
    battery_active_power_ratio_peak = 0.0
    price_temp = 0.0
    arbitrage_sensitivity = 0.0
    res_price_up_temp = 0.0
    res_price_down_temp = 0.0
    res_up_sensitivity = 0.0
    res_down_sensitivity = 0.0
    # if things go haywire then we have some initialized values
    new_grid_load = 0.0
    new_grid_reactive_power = 0.0
    # new_SoC = 0.0
    new_battery_reactive_power = 0.0
    arbitrage_purchased_power_actual = 0.0
    arbitrage_purchased_power_ideal = 0.0
    x_val = []

    # creating dictionaries which will save results
    da_variables = {'Time': [], 'battery_setpoints_da': [], 'SoC_da': [], 'grid_load_da': [], 'peak_load_da': [],
                    'react_grid_da': [], 'react_batt_da': [], 'grid_pf_da': [], 'total_load_predict_da': [],
                    'price_predict_da': [], 'arbitrage_purchased_power_da': [], 'reg_up_cap_da': [], 'reg_down_cap_da': [], 'reg_price_predict_up': [], 'reg_price_predict_down': []}
    rt_variables = {'Time': [], 'battery_setpoints_rt': [], 'SoC_rt': [], 'grid_load_rt': [], 'peak_load_rt': [],
                    'react_grid_rt': [], 'react_batt_rt': [], 'grid_pf_rt': [], 'total_load_actual_rt': [],
                    'price_actual_rt': [], 'arbitrage_purchased_power_ideal_rt': [], 'arbitrage_purchased_power_actual_rt': [],
                    'reg_price_up_rt': [], 'reg_price_down_rt': [],'reg_up_cap_rt': [], 'reg_down_cap_rt': []}
    #TODO: add reserve capacity metric
    metrics = {'Time': [], 'arbitrage_revenue_da': [], 'peak_surcharge_da': [], 'arbitrage_revenue_ideal_rt': [], 'arbitrage_revenue_actual_rt': [], 'peak_surcharge_rt': [], 'original_surcharge': [],
               'reg_up_rev_da': [], 'reg_down_rev_da': [], 'reg_up_rev_rt': [], 'reg_down_rev_rt': []}

    while ts < simulation_duration:
        print('current time -> ' + str(current_time))

        # Hourly Optimization Routine
        if (ts % (60*60)) == 0:
            # print('current time -> ' + str(current_time))
            print("Performing Day-Ahead Optimization")

            next_day_hourly_interval = timedelta(days=+1)
            day_ahead_forecast_horizon = current_time + next_day_hourly_interval

            battery_obj.set_hourly_load_forecast(current_time, day_ahead_forecast_horizon, ts)

            if battery_obj.use_case_dict['energy_arbitrage']['control_type'] == 'opti-based':
                battery_obj.set_hourly_price_forecast(current_time, day_ahead_forecast_horizon, ts)

            if battery_obj.use_case_dict['reserves_placement']['control_type'] == 'opti-based':
                battery_obj.set_hourly_res_price_forecast(current_time, day_ahead_forecast_horizon, ts)

            print("Solving the Day-Ahead Optimization Problem")

            if ts > 0:
                battery_obj.set_SoC(battery_obj.SoC_actual[ts-1])

            battery_obj.DA_optimal_quantities()

            print("Battery-Setpoints (kW) -> "+str(battery_obj.battery_setpoints_prediction))
            if battery_obj.use_case_dict['reserves_placement']['control_type'] == 'opti-based':
                print("Battery-Res Up (kWh) -> "+str(battery_obj.battery_res_up_prediction))
                print("Battery-Res Down (kWh) -> "+str(battery_obj.battery_res_down_prediction))

            print("Battery-SoC (kWh)-> "+str(battery_obj.SoC_prediction))
            print("PeakLoad (kW) -> "+str(battery_obj.peak_load_prediction))
            print("GridLoad (kW) -> "+str(battery_obj.grid_load_prediction))
            print("GridReact (kVar) -> "+str(battery_obj.grid_react_power_prediction))
            print("BattReact (kVar) -> "+str(battery_obj.battery_react_power_prediction))
            # print("ResPriceUp ($/kWh) -> "+str(battery_obj.res_price_predict_up))
            # print("ResPriceDown ($/kWh) -> "+str(battery_obj.res_price_predict_down))


            new_battery_setpoint = battery_obj.battery_setpoints_prediction[0]
            new_reserve_up_cap = battery_obj.battery_res_up_prediction[0]*5/60  # per 5 minute of an hour
            new_reserve_down_cap = battery_obj.battery_res_down_prediction[0]*5/60  # per 5 minute of an hour
            if ts > 0:
                load_temp = battery_obj.actual_load[ts-1]
            else:
                load_temp = battery_obj.load_predict[0]
            load_react_temp = battery_obj.load_predict[0]*battery_obj.load_pf
            grid_act_power_temp = battery_obj.grid_load_prediction[0]
            grid_react_power_temp = battery_obj.grid_react_power_prediction[0]
            batt_react_power_temp = battery_obj.battery_react_power_prediction[0]

            if battery_obj.use_case_dict['energy_arbitrage']['control_type'] == 'opti-based':

                price_temp = battery_obj.price_predict[0]
                arbitrage_sensitivity = abs(((max(battery_obj.battery_setpoints_prediction) - min(battery_obj.battery_setpoints_prediction)) / np.std(battery_obj.battery_setpoints_prediction))) / \
                                        (abs(max(battery_obj.price_predict) - min(battery_obj.price_predict)) / np.std(np.array(battery_obj.price_predict)))

                # arbitrage_sensitivity = ((max(battery_obj.battery_setpoints_prediction) - min(battery_obj.battery_setpoints_prediction))) / \
                #                         (abs(max(battery_obj.price_predict) - min(battery_obj.price_predict)) / np.std(np.array(battery_obj.price_predict)))

            if battery_obj.use_case_dict['reserves_placement']['control_type'] == 'opti-based':
                res_price_up_temp = battery_obj.res_price_predict_up[0]
                if np.std(battery_obj.battery_res_up_prediction) == 0.0:
                    res_up_sensitivity = 0.5
                else:
                    res_up_sensitivity = ((max(battery_obj.battery_res_up_prediction) - min(
                        battery_obj.battery_res_up_prediction)) / np.std(battery_obj.battery_res_up_prediction)) / \
                                            (abs(max(battery_obj.res_price_predict_up) - min(battery_obj.res_price_predict_up)) / np.std(
                                                np.array(battery_obj.res_price_predict_up)))
                res_price_down_temp = battery_obj.res_price_predict_down[0]

                if np.std(battery_obj.battery_res_down_prediction)  == 0.0:
                    res_down_sensitivity = 0.5
                else:
                    res_down_sensitivity = ((max(battery_obj.battery_res_down_prediction) - min(
                        battery_obj.battery_res_down_prediction)) / np.std(battery_obj.battery_res_down_prediction)) / \
                                         (abs(max(battery_obj.res_price_predict_down) - min(
                                             battery_obj.res_price_predict_down)) / np.std(
                                             np.array(battery_obj.res_price_predict_down)))
                # res_up_sensitivity = ((max(battery_obj.battery_res_up_prediction) - min(
                #     battery_obj.battery_res_up_prediction))) / \
                #                      (abs(max(battery_obj.res_price_predict_up) - min(
                #                          battery_obj.res_price_predict_up)) / np.std(
                #                          np.array(battery_obj.res_price_predict_up)))
                # res_price_down_temp = battery_obj.res_price_predict_down[0]
                # res_down_sensitivity = ((max(battery_obj.battery_res_down_prediction) - min(
                #     battery_obj.battery_res_down_prediction))) / \
                #                        (abs(max(battery_obj.res_price_predict_down) - min(
                #                            battery_obj.res_price_predict_down)) / np.std(
                #                            np.array(battery_obj.res_price_predict_down)))

            battery_react_power_ratio = (battery_obj.battery_react_power_prediction[0] / (battery_obj.grid_react_power_prediction[0] + battery_obj.battery_react_power_prediction[0]))
            grid_react_power_ratio = 1 - battery_react_power_ratio
            if battery_obj.grid_load_prediction[0] == 0.0:
                battery_active_power_ratio_peak = 1.0
            else:
                battery_active_power_ratio_peak = (abs(max(battery_obj.battery_setpoints_prediction)-min(battery_obj.battery_setpoints_prediction))/np.std(battery_obj.battery_setpoints_prediction)) / (abs(max(battery_obj.grid_load_prediction) - min(battery_obj.grid_load_prediction)) / np.std(np.array(battery_obj.grid_load_prediction)))

            if ts > 0:
                rt_variables['Time'].append(x_val)
                # rt_variables['ts'].append(ts)
                rt_variables['battery_setpoints_rt'].append(battery_obj.battery_setpoints_actual[ts - 60*60:ts])
                rt_variables['SoC_rt'].append(battery_obj.SoC_actual[ts-60*60:ts])
                rt_variables['grid_load_rt'].append(battery_obj.grid_load_actual[ts-60*60:ts])
                rt_variables['peak_load_rt'].append([max(battery_obj.grid_load_actual[ts-60*60:ts])] * 60*60)
                rt_variables['react_grid_rt'].append(battery_obj.grid_react_power_actual[ts-60*60:ts])
                rt_variables['react_batt_rt'].append(battery_obj.battery_react_power_actual[ts-60*60:ts])
                rt_variables['grid_pf_rt'].append(battery_obj.grid_power_factor_actual[ts-60*60:ts])
                rt_variables['total_load_actual_rt'].append(battery_obj.actual_load[ts-60*60:ts])
                rt_variables['price_actual_rt'].append(battery_obj.actual_price[ts-60*60:ts])
                rt_variables['arbitrage_purchased_power_ideal_rt'].append(battery_obj.arbitrage_purchased_power_ideal_rt[ts-60*60:ts])
                rt_variables['arbitrage_purchased_power_actual_rt'].append(battery_obj.arbitrage_purchased_power_actual_rt[ts-60*60:ts])
                rt_variables['reg_up_cap_rt'].append(battery_obj.battery_res_up_cap_actual[ts-60*60:ts])
                rt_variables['reg_down_cap_rt'].append(battery_obj.battery_res_down_cap_actual[ts-60*60:ts])
                rt_variables['reg_price_up_rt'].append(battery_obj.actual_res_price_up[ts-60*60:ts])
                rt_variables['reg_price_down_rt'].append(battery_obj.actual_res_price_down[ts-60*60:ts])
                x_val = []

            if ((ts % battery_obj.reporting_frequency) == 0) and (ts > 1):
                idx = np.arange(0, 3600, 300)
                metrics['Time'].append(ts)
                metrics['arbitrage_revenue_da'].append(np.sum(np.multiply(np.array(da_variables['arbitrage_purchased_power_da'])[:, 0], np.array(da_variables['price_predict_da'])[:, 0])))
                metrics['arbitrage_revenue_ideal_rt'].append(np.sum(np.multiply(np.array(rt_variables['arbitrage_purchased_power_ideal_rt'])[:, idx], np.array(rt_variables['price_actual_rt'])[:, idx]))*5/60)
                metrics['arbitrage_revenue_actual_rt'].append(np.sum(np.multiply(np.array(rt_variables['arbitrage_purchased_power_actual_rt'])[:, idx], np.array(rt_variables['price_actual_rt'])[:, idx]))*5/60)
                metrics['peak_surcharge_rt'].append(np.max(np.array(rt_variables['peak_load_rt']))*battery_obj.peak_price)
                metrics['peak_surcharge_da'].append(np.max(np.array(da_variables['peak_load_da']))*battery_obj.peak_price)
                metrics['original_surcharge'].append(np.max(np.array(rt_variables['total_load_actual_rt']))*battery_obj.peak_price)
                metrics['reg_up_rev_da'].append(np.sum(np.multiply(np.array(da_variables['reg_up_cap_da'])[:, 0], np.array(da_variables['reg_price_predict_up'])[:, 0])))
                metrics['reg_down_rev_da'].append(np.sum(np.multiply(np.array(da_variables['reg_down_cap_da'])[:, 0], np.array(da_variables['reg_price_predict_down'])[:, 0])))
                metrics['reg_up_rev_rt'].append(np.sum(np.multiply(np.array(rt_variables['reg_up_cap_rt'])[:, idx], np.array(rt_variables['reg_price_up_rt'])[:, idx]))*5/60)
                metrics['reg_down_rev_rt'].append(np.sum(np.multiply(np.array(rt_variables['reg_down_cap_rt'])[:, idx], np.array(rt_variables['reg_price_down_rt'])[:, idx]))*5/60)
                store_dict_to_json(ts, da_variables, 'da')
                store_dict_to_json(ts, rt_variables, 'rt')
                store_dict_to_json(ts, metrics, 'results')
                da_variables = clean_dict(da_variables, 'da')
                rt_variables = clean_dict(rt_variables, 'rt')
                metrics = clean_dict(metrics, 'results')
            da_variables['Time'].append(ts)
            da_variables['battery_setpoints_da'].append([battery_obj.battery_setpoints_prediction[0]]*60*60)
            da_variables['SoC_da'].append([battery_obj.SoC_prediction[0]]*60*60)
            da_variables['grid_load_da'].append([battery_obj.grid_load_prediction[0]]*60*60)
            da_variables['peak_load_da'].append([battery_obj.peak_load_prediction]*60*60)
            da_variables['react_grid_da'].append([battery_obj.grid_react_power_prediction[0]]*60*60)
            da_variables['react_batt_da'].append([battery_obj.battery_react_power_prediction[0]]*60*60)
            da_variables['grid_pf_da'].append([battery_obj.grid_power_factor_prediction[0]]*60*60)
            da_variables['total_load_predict_da'].append([battery_obj.load_predict[0]]*60*60)
            da_variables['price_predict_da'].append([battery_obj.price_predict[0]]*60*60)
            da_variables['arbitrage_purchased_power_da'].append([battery_obj.battery_setpoints_prediction[0]]*60*60)
            da_variables['reg_price_predict_up'].append([battery_obj.res_price_predict_up[0]]*60*60)
            da_variables['reg_price_predict_down'].append([battery_obj.res_price_predict_down[0]]*60*60)
            da_variables['reg_up_cap_da'].append([battery_obj.battery_res_up_prediction[0]]*60*60)
            da_variables['reg_down_cap_da'].append([battery_obj.battery_res_down_prediction[0]]*60*60)

        # RealTime Control Routine
        # get updated load profile
        # battery_obj.set_load_actual(load_temp, (battery_obj.load_predict[1]-battery_obj.load_predict[0])*battery_obj.hrs_to_secs/2 )

        # battery_obj.set_load_actual(load_temp, np.mean(np.diff(battery_obj.load_predict[0:10])) * battery_obj.hrs_to_secs)

        battery_obj.set_load_actual(load_temp, np.mean(np.diff(battery_obj.load_predict[0:3])) * battery_obj.hrs_to_secs)


        # print(str(current_time) + "-->" + " Actual active power load: " + str(battery_obj.actual_load[ts]))
        # print(str(current_time) + "-->" + " Actual reactive power load: " + str(battery_obj.actual_reactive_load[ts]))

        # get mismatch from the prediction
        active_power_mismatch = battery_obj.actual_load[ts] - load_temp
        # print(str(current_time) + "-->" + " Act-Power Mismatch: " + str(active_power_mismatch))
        reactive_power_mismatch = battery_obj.actual_reactive_load[ts] - load_react_temp
        # print(str(current_time) + "-->" + " React-Power Mismatch: " + str(reactive_power_mismatch))

        if battery_obj.use_case_dict['energy_arbitrage']['control_type'] == 'opti-based':
            battery_obj.set_price_actual(price_temp, (battery_obj.price_predict[1]-battery_obj.price_predict[0])*300*battery_obj.hrs_to_secs, ts)
        else:
            battery_obj.actual_price.append(price_temp)

        if battery_obj.use_case_dict['reserves_placement']['control_type'] == 'opti-based':
            battery_obj.get_reg_signal(current_time, ts)
            battery_obj.set_res_price_actual(res_price_up_temp,
                                             res_price_down_temp,
                                             (battery_obj.res_price_predict_up[1] - battery_obj.res_price_predict_up[
                                                 0]) * 300 * battery_obj.hrs_to_secs,
                                             (battery_obj.res_price_predict_down[1] - battery_obj.res_price_predict_down[
                                                 0]) * 300 * battery_obj.hrs_to_secs,
                                             ts)
        else:
            battery_obj.actual_res_price_up.append(res_price_down_temp)
            battery_obj.actual_res_price_down.append(res_price_down_temp)


        # check if external signal has been imposed

        # iterate through priority
        #TODO: more robust method of prioritizing the list
        for i in range(0, len(services_list)-1):
            try:
                service_request = services_list[priority_list.index(i + 1)]

                if service_request == "demand_charge":
                    # check demand charge reduction in real-time
                    new_SoC, new_battery_setpoint, new_grid_load = battery_obj.rtc_demand_charge_reduction \
                        (active_power_mismatch,
                         new_battery_setpoint,
                         new_SoC,
                         battery_obj.actual_load[ts],
                         batt_react_power_temp,
                         battery_active_power_ratio_peak)

                elif service_request == "power_factor_correction":

                    new_battery_reactive_power, new_grid_reactive_power, apparant_temp, pf_temp = battery_obj.rtc_power_factor_correction\
                        (batt_react_power_temp,
                         grid_react_power_temp,
                         reactive_power_mismatch,
                         battery_react_power_ratio,
                         grid_react_power_ratio,
                         grid_act_power_temp)

                elif service_request == "energy_arbitrage":
                    if (ts % 300) == 0:     # decide arbitrage power
                        if battery_obj.use_case_dict['energy_arbitrage']['control_type'] == 'opti-based':
                            price_mismatch = (battery_obj.actual_price[ts] - battery_obj.price_predict[0])

                            # print(str(current_time) + "-->" + " Energy Price Mismatch: " + str(price_mismatch))
                            if (price_mismatch > 0.0) and (new_battery_setpoint > 0.0):
                                delP = arbitrage_sensitivity*price_mismatch
                            elif (price_mismatch < 0.0) and (new_battery_setpoint < 0.0):
                                delP = arbitrage_sensitivity*price_mismatch
                            else:
                                delP = 0.0
                            # new_battery_setpoint = new_battery_setpoint + arbitrage_sensitivity*price_mismatch
                            new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint, delP)
                            # check SoC
                            new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
                            # new grid load
                            new_grid_load = max(0, battery_obj.actual_load[ts] - new_battery_setpoint)
                            arbitrage_purchased_power_ideal = new_battery_setpoint
                            arbitrage_purchased_power_actual = new_battery_setpoint
                        if ts > 0:
                            battery_obj.arbitrage_purchased_power_actual_rt[ts-300:ts] = [min(abs(battery_obj.arbitrage_purchased_power_actual_rt[ts-300:ts]))]*300
                    # if PRIORITY is True:   # maintain arbitrage threshold
                elif service_request == "reserves_placement":
                    if (ts % 300) == 0:     # decide reserve purchase power
                        if battery_obj.use_case_dict['reserves_placement']['control_type'] == 'opti-based':
                            res_price_up_mismatch = (battery_obj.actual_res_price_up[ts] - battery_obj.res_price_predict_up[0])
                            res_price_down_mismatch = (battery_obj.actual_res_price_down[ts] - battery_obj.res_price_predict_down[0])
                            # print(str(current_time) + "-->" + " Reserve Price Up Mismatch: " + str(res_price_up_mismatch))
                            # print(str(current_time) + "-->" + " Reserve Price Down Mismatch: " + str(res_price_down_mismatch))

                            # if res_price_up_mismatch > 0.0:
                            # new_reserve_up_cap = min((battery_obj.rated_kWh - battery_obj.reserve_SoC),
                            #                          max(battery_obj.reserve_SoC,
                            #                             new_reserve_up_cap + (res_price_up_mismatch * res_up_sensitivity)))
                            if res_price_up_mismatch > 0.0:
                                new_reserve_up_cap += (res_price_up_mismatch * res_up_sensitivity)
                            # if new_reserve_up_cap > (battery_obj.rated_kWh - battery_obj.reserve_SoC):
                            #     new_reserve_up_cap = battery_obj.rated_kWh - battery_obj.reserve_SoC
                            # elif  new_reserve_up_cap < battery_obj.reserve_SoC:
                            #     new_reserve_up_cap = battery_obj.reserve_SoC

                            # temp = new_SoC - (battery_obj.battery_setpoints_prediction[0] * battery_obj.hrs_to_secs * 299) - (new_reserve_up_cap/battery_obj.bat_eta) * battery_obj.hrs_to_secs * 299
                            # this is a check that with this SoC will we violate the SoC range in the next hour or not?
                            # temp = new_SoC - new_reserve_up_cap*(60/5)
                            # if temp < battery_obj.reserve_SoC:
                            #     # new_reserve_up_cap = new_reserve_up_cap - (battery_obj.bat_eta * (-battery_obj.reserve_SoC + new_SoC - (battery_obj.battery_setpoints_prediction[0] * battery_obj.hrs_to_secs * 299) ) / (battery_obj.hrs_to_secs * 300))
                            #     new_reserve_up_cap -= (battery_obj.reserve_SoC-temp)*5/60
                        # if res_price_down_mismatch > 0.0:
                        #     new_reserve_down_cap = min((battery_obj.rated_kWh - battery_obj.reserve_SoC),
                        #                              max(battery_obj.reserve_SoC,
                        #                                 new_reserve_down_cap + (res_price_down_mismatch * res_down_sensitivity)))
                            if res_price_down_mismatch > 0.0:
                                new_reserve_down_cap += (res_price_down_mismatch * res_down_sensitivity)
                            # temp = new_SoC + (battery_obj.battery_setpoints_prediction[0] * battery_obj.hrs_to_secs * 299) + (new_reserve_down_cap*battery_obj.bat_eta) * battery_obj.hrs_to_secs * 299
                            # temp = new_SoC + new_reserve_down_cap*(60/5)
                            # if temp > (battery_obj.rated_kWh-battery_obj.reserve_SoC):
                            #     new_reserve_down_cap -= (temp-battery_obj.rated_kWh+battery_obj.reserve_SoC)*5/60

                                # new_reserve_down_cap = new_reserve_down_cap - ((battery_obj.rated_kWh - battery_obj.reserve_SoC - new_SoC + (battery_obj.battery_setpoints_prediction[0] * battery_obj.hrs_to_secs * 299) ) / ( battery_obj.bat_eta * battery_obj.hrs_to_secs * 300))


                            # print(str(current_time) + "-->" + " Reserve Up Capacity Realtime: " + str(new_reserve_up_cap) + " predicted: " + str(battery_obj.battery_res_up_prediction[0]*5/60))
                            # print(str(current_time) + "-->" + " Reserve Down Capacity Realtime: " + str(new_reserve_down_cap) + " predicted: " + str(battery_obj.battery_res_down_prediction[0]*5/60))

                    if battery_obj.actual_reg_signal[ts] < 0.0:
                        # below the complicated 0.5/(5*60) comes from conversion of capacity to power
                        # 0.5 comes from the fact the signal is coming every 2 second, (5*60) because capacity is given for every 5 minutes
                        new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                                                                           battery_obj.actual_reg_signal[ts] * new_reserve_down_cap*(1/(5*60)))
                        # new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                        #                                                    battery_obj.actual_reg_signal[ts] * new_reserve_down_cap/(battery_obj.res_eta_down*60/5))

                        new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
                        # print(str(current_time) + "-->" + " Regulation Signal: " + str(
                        #     battery_obj.actual_reg_signal[ts] * new_reserve_down_cap*(0.5/(5*60)))+ ': reg_down_cap: ' + str(new_reserve_down_cap) + 'batt_sp' + str(new_battery_setpoint))

                    elif battery_obj.actual_reg_signal[ts] > 0.0:
                        new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                                                                           battery_obj.actual_reg_signal[ts] * new_reserve_up_cap*(1/(5*60)))
                        # new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                        #                                                    battery_obj.actual_reg_signal[ts] * new_reserve_up_cap/(battery_obj.res_eta_up*60/5))
                        new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
                        # print(str(current_time) + "-->" + " Regulation Signal: " + str(
                        #     battery_obj.actual_reg_signal[ts] * new_reserve_up_cap *(0.5/(5*60))) + ': reg_up_cap: ' + str(new_reserve_up_cap) + 'batt_sp' + str(new_battery_setpoint))
            except:
                pass

        top_priority_service_request = services_list[priority_list.index(1)]

        if (top_priority_service_request == "demand_charge"):
            print("Demand Charge is the highest priority")
            if new_grid_load > battery_obj.peak_load_prediction:
                # print("demand charge is the top prioirity but the peak load is getting violated")
                # adjust battery power setpoint and see whether the adjusted power is even physically possible
                new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint, new_grid_load-battery_obj.peak_load_prediction)
                # check SoC
                new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
                # new grid load
                new_grid_load = max(0, battery_obj.actual_load[ts] - new_battery_setpoint)

                # check grid loading
                if new_grid_load == 0:
                    # new_battery_setpoints = set_point_prediction
                    new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
                    # since demand charge was the priority, arbitrage power may have been violated

            if arbitrage_purchased_power_ideal > 0:
                arbitrage_purchased_power_actual = min(arbitrage_purchased_power_actual, new_battery_setpoint)
            elif arbitrage_purchased_power_ideal < 0:
                arbitrage_purchased_power_actual = max(arbitrage_purchased_power_actual, new_battery_setpoint)
            # print("arbitrage_purchased_power_actual" + str(arbitrage_purchased_power_actual))
            # print("arbitrage_purchased_power_ideal" + str(arbitrage_purchased_power_ideal))
            # print("new_battery_setpoint" + str(new_battery_setpoint))

        elif (top_priority_service_request == "power_factor_correction"):
            if abs(pf_temp) - battery_obj.pf_limit < 0.05:
                print("power factor is below the limit -- controlling it as it's the highest priority")
                new_battery_reactive_power = (np.sqrt(
                    (grid_act_power_temp ** 2) * (1 / (battery_obj.grid_power_factor_prediction[0] ** 2)) - (
                                (grid_act_power_temp) ** 2)))
                apparant_temp = battery_obj.get_apparent_power(grid_act_power_temp, new_battery_reactive_power)
                pf_temp = battery_obj.get_power_factor(grid_act_power_temp, apparant_temp)
                if (np.sqrt(new_battery_reactive_power**2 + new_battery_setpoint**2) > battery_obj.rated_inverter_kVA):
                    # print("reactive power change has violated the rated inverter kVA")
                    new_battery_setpoint = np.sqrt(battery_obj.rated_inverter_kVA**2 - new_battery_reactive_power**2)
            else:
                print("power factor is within the tolerance of limit of " + str(battery_obj.pf_limit))

        elif (top_priority_service_request == "energy_arbitrage"):

            if arbitrage_purchased_power_ideal > 0:  # we have asked to discharge the battery
                if new_battery_setpoint < arbitrage_purchased_power_ideal:
                    new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                                                                       arbitrage_purchased_power_ideal - new_battery_setpoint)
                    new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
                    new_grid_load = max(0, battery_obj.actual_load[ts] - new_battery_setpoint)
            elif arbitrage_purchased_power_ideal < 0:  # we asked for charging power
                if new_battery_setpoint > arbitrage_purchased_power_ideal:
                    new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
                                                                       arbitrage_purchased_power_ideal - new_battery_setpoint)
                    new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
                    new_grid_load = max(0, battery_obj.actual_load[ts] - new_battery_setpoint)
            arbitrage_purchased_power_actual = new_battery_setpoint

        # elif (top_priority_service_request == "reserves_placement"):
        #         res_up_mismatch =  ideal_reserve_up_cap - battery_obj.battery_res_up_prediction[0]
        #
        #         new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
        #                                                            arbitrage_purchased_power_ideal - new_battery_setpoint)
        #
        #         if new_battery_setpoint < arbitrage_purchased_power_ideal:
        #             new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
        #                                                                arbitrage_purchased_power_ideal - new_battery_setpoint)
        #             new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
        #             new_grid_load = max(0, battery_obj.actual_load[ts] - new_battery_setpoint)
        #     elif arbitrage_purchased_power_ideal < 0:  # we asked for charging power
        #         if new_battery_setpoint > arbitrage_purchased_power_ideal:
        #             new_battery_setpoint = battery_obj.change_setpoint(new_battery_setpoint,
        #                                                                arbitrage_purchased_power_ideal - new_battery_setpoint)
        #             new_SoC, new_battery_setpoint = battery_obj.check_SoC(new_battery_setpoint, new_SoC)
        #             new_grid_load = max(0, battery_obj.actual_load[ts] - new_battery_setpoint)
        #     arbitrage_purchased_power_actual = new_battery_setpoint
        #
        #     ideal_reserve_up_cap = new_reserve_up_cap
        #     ideal_reserve_down_cap = new_reserve_down_cap


        # print("----------- Real-Time Control Done --------")
        battery_obj.SoC_actual.append(new_SoC)
        battery_obj.battery_setpoints_actual.append(new_battery_setpoint)
        battery_obj.grid_load_actual.append(new_grid_load)
        battery_obj.battery_react_power_actual.append(new_battery_reactive_power)
        battery_obj.grid_react_power_actual.append(new_grid_reactive_power)
        battery_obj.grid_apparent_power_actual.append(battery_obj.get_apparent_power(new_grid_load, battery_obj.grid_react_power_actual[ts]))
        battery_obj.grid_power_factor_actual.append(battery_obj.get_power_factor(new_grid_load, battery_obj.grid_apparent_power_actual[ts]))
        battery_obj.battery_res_up_cap_actual.append(new_reserve_up_cap*60/5)
        battery_obj.battery_res_down_cap_actual.append(new_reserve_down_cap*60/5)
        if (arbitrage_purchased_power_actual > new_battery_setpoint) and arbitrage_purchased_power_actual > 0:
            check_point = 1

        battery_obj.arbitrage_purchased_power_actual_rt.append(arbitrage_purchased_power_actual)
        battery_obj.arbitrage_purchased_power_ideal_rt.append(arbitrage_purchased_power_ideal)
        load_temp = battery_obj.actual_load[ts]
        price_temp = battery_obj.actual_price[ts]
        load_react_temp = battery_obj.actual_reactive_load[ts]
        grid_act_power_temp = new_grid_load
        grid_react_power_temp = new_grid_reactive_power
        batt_react_power_temp = new_battery_reactive_power
        res_price_up_temp = battery_obj.actual_res_price_up[ts]
        res_price_down_temp = battery_obj.actual_res_price_down[ts]

        if (battery_obj.battery_setpoints_actual[ts] > 740.0) or (battery_obj.battery_setpoints_actual[ts] < -740.0):
            check_point = 1
        # print(str(current_time) + "-->" + " Current Active Power Battery Setpoint: " + str(battery_obj.battery_setpoints_actual[ts]))
        # print(str(current_time) + "-->" + " Current Battery SoC: " + str(battery_obj.SoC_actual[ts]))
        #
        # print(str(current_time) + "-->" + " Current Reactive Power from Battery: " + str(battery_obj.battery_react_power_actual[ts]))
        # print(str(current_time) + "-->" + " Current Reactive Power from Grid: " + str(battery_obj.grid_react_power_actual[ts]))
        # print(str(current_time) + "-->" + " Total Reactive Power from Load: " + str(battery_obj.load_pf*new_grid_load))

        x_val.append(ts)

        current_time = current_time + timedelta(seconds=+1)

        ts += 1



