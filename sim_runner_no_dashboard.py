import os
import sys
import json
import numpy as np
from datetime import datetime, timedelta
from battery_class_new import battery_class_new
import matplotlib.animation as ani
import matplotlib.pyplot as plt


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
    with open("results_folder\\" + str(ts) + '_' + id + '.json', 'w') as fp:
        json.dump(variables, fp)


def clean_dict(dict, id):
    if id == "da":
        dict = {'Time': [], 'battery_setpoints_da': [], 'SoC_da': [], 'grid_load_da': [],
                        'peak_load_da': [],
                        'react_grid_da': [], 'react_batt_da': [], 'grid_pf_da': [], 'total_load_predict_da': []}
    elif id == "rt":
        dict = {'Time': [], 'battery_setpoints_rt': [], 'SoC_rt': [], 'grid_load_rt': [],
                        'peak_load_rt': [],
                        'react_grid_rt': [], 'react_batt_rt': [], 'grid_pf_rt': [], 'total_load_actual_rt': []}
    return dict


if __name__ == "__main__":

    pre_file = 'results_folder\\'
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
    SoC_temp = battery_obj.SoC_init
    new_battery_setpoint = 0.0

    # if things go haywire then we have some initialized values
    new_grid_load = 0.0
    new_SoC = 0.0
    new_battery_reactive_power = 0.0
    x_val = []

    # creating dictionaries which will save results
    da_variables = {'Time': [], 'battery_setpoints_da': [], 'SoC_da': [], 'grid_load_da': [], 'peak_load_da': [], 'react_grid_da': [], 'react_batt_da': [], 'grid_pf_da': [], 'total_load_predict_da': []}
    rt_variables = {'Time': [], 'battery_setpoints_rt': [], 'SoC_rt': [], 'grid_load_rt': [], 'peak_load_rt': [], 'react_grid_rt': [], 'react_batt_rt': [], 'grid_pf_rt': [], 'total_load_actual_rt': []}

    # fig, ax = plt.subplots()

    while ts < simulation_duration:
        print('------------------------<- current time ->----------------------- ' + str(current_time))
        # battery_obj.SoC_actual.append(battery_obj.SoC_init)
        # Hourly Optimization Routine
        if (ts % (60*60)) == 0:
            # print('current time -> ' + str(current_time))
            print("Performing Day-Ahead Optimization")

            next_day_hourly_interval = timedelta(days=+1)
            day_ahead_forecast_horizon = current_time + next_day_hourly_interval

            battery_obj.set_hourly_load_forecast(current_time, day_ahead_forecast_horizon)


            print("Solving the Day-Ahead Optimization Problem")

            if ts > 0:
                battery_obj.set_SoC(battery_obj.SoC_actual[ts-1])

            battery_obj.DA_optimal_quantities()

            print("Battery-Setpoints (kW) -> "+str(battery_obj.battery_setpoints_prediction))
            print("Battery-SoC (kWh)-> "+str(battery_obj.SoC_prediction))
            print("PeakLoad (kW) -> "+str(battery_obj.peak_load_prediction))
            print("GridLoad (kW) -> "+str(battery_obj.grid_load_prediction))
            print("GridReact (kVar) -> "+str(battery_obj.grid_react_power_prediction))
            print("BattReact (kVar) -> "+str(battery_obj.battery_react_power_prediction))

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
                x_val = []

            if ((ts % battery_obj.reporting_frequency) == 0) and (ts > 1):
                store_dict_to_json(ts, da_variables, 'da')
                store_dict_to_json(ts, rt_variables, 'rt')
                da_variables = clean_dict(da_variables, 'da')
                rt_variables = clean_dict(rt_variables, 'rt')

            da_variables['Time'].append(ts)
            da_variables['battery_setpoints_da'].append([battery_obj.battery_setpoints_prediction[0]]*60*60)
            da_variables['SoC_da'].append([battery_obj.SoC_prediction[0]]*60*60)
            da_variables['grid_load_da'].append([battery_obj.grid_load_prediction[0]]*60*60)
            da_variables['peak_load_da'].append([battery_obj.peak_load_prediction]*60*60)
            da_variables['react_grid_da'].append([battery_obj.grid_react_power_prediction[0]]*60*60)
            da_variables['react_batt_da'].append([battery_obj.battery_react_power_prediction[0]]*60*60)
            da_variables['grid_pf_da'].append([battery_obj.grid_power_factor_prediction[0]]*60*60)
            da_variables['total_load_predict_da'].append([battery_obj.load_up[0]]*60*60)



        # RealTime Control Routine
        # get updated load profile
        battery_obj.set_load_actual(battery_obj.load_predict[0])
        print(str(current_time) + "-->" + " Actual load: " + str(battery_obj.actual_load[ts]))

        # get mismatch from the prediction
        if ts==0:
            print("Actual Load", battery_obj.actual_load)
        active_power_mismatch = battery_obj.actual_load[ts] - battery_obj.load_up[0]
        print(str(current_time) + "-->" + " Act-Power Mismatch: " + str(active_power_mismatch))
        reactive_power_mismatch = battery_obj.load_pf*active_power_mismatch
        print(str(current_time) + "-->" + " React-Power Mismatch: " + str(reactive_power_mismatch))

        # check if external signal has been imposed

        # check service priority

        # iterate through priority
        for i in range(0, len(services_list)-1):
            service_priority = services_list[priority_list.index(i + 1)]
            if service_priority == "demand_charge":
                # check demand charge reduction in real-time
                new_SoC, new_battery_setpoint, new_grid_load = battery_obj.rtc_demand_charge_reduction\
                    (i, active_power_mismatch, battery_obj.battery_setpoints_prediction[0], SoC_temp, battery_obj.actual_load[ts])

            elif service_priority == "power_factor_correction":
                if i == 0: # highest priority
                    print("Power Factor Correction is the highest priority")

                else:
                    # this means that actually load power is lower than expected, hence the reactive power drawn is also less
                    # ratio of the battery from the total reactive mismatch
                    battery_ratio = (1 - battery_obj.battery_react_power_prediction[0] / (battery_obj.grid_react_power_prediction[0]+battery_obj.battery_react_power_prediction[0]))

                    new_battery_reactive_power = battery_obj.battery_react_power_prediction[0] + battery_ratio*reactive_power_mismatch


                    print("Power Factor Correction is the priority number " + str(i+1))

            elif service_priority == "energy_arbitrage":
                if i == 0: # highest priority
                    print("Energy Arbitrage is the highest priority")

                else:
                    print("Energy Arbitrage is the priority number " + str(i+1))

            elif service_priority == "reserves_placement":
                if i == 0: # highest priority
                    print("Reserve Placement is the highest priority")

                else:
                    print("Reserve Placement is the priority number" + str(i+1))



        print("----------- Real-Time Control Done --------")
        battery_obj.SoC_actual.append(SoC_temp)
        battery_obj.battery_setpoints_actual.append(new_battery_setpoint)
        battery_obj.grid_load_actual.append(new_grid_load)
        battery_obj.battery_react_power_actual.append(new_battery_reactive_power)
        battery_obj.grid_react_power_actual.append(battery_obj.load_pf*new_grid_load + new_battery_reactive_power)
        battery_obj.grid_apparent_power_actual.append(battery_obj.get_apparent_power(new_grid_load, battery_obj.grid_react_power_actual[ts]))
        battery_obj.grid_power_factor_actual.append(battery_obj.get_power_factor(new_grid_load, battery_obj.grid_apparent_power_actual[ts]))
        SoC_temp = new_SoC
        print(str(current_time) + "-->" + " Current Active Power Battery Setpoint: " + str(battery_obj.battery_setpoints_actual[ts]))
        print(str(current_time) + "-->" + " Current Battery SoC: " + str(battery_obj.SoC_actual[ts]))

        print(str(current_time) + "-->" + " Current Reactive Power from Battery: " + str(battery_obj.battery_react_power_actual[ts]))
        print(str(current_time) + "-->" + " Current Reactive Power from Grid: " + str(battery_obj.grid_react_power_actual[ts]))
        print(str(current_time) + "-->" + " Total Reactive Power from Load: " + str(battery_obj.load_pf*new_grid_load))

        x_val.append(ts)
        # animate(battery_obj.battery_setpoints_actual[ts])
        # p = ax.plot(x_val[0:ts+1], battery_obj.battery_setpoints_actual[0:ts+1], label='Battery Power (Charge/Discharge)', color='b')
        # # ax.plot([battery_obj.peak_load_prediction] * battery_obj.windowLength, label='Peak load')
        # # ax.plot(battery_obj.grid_load_prediction, label='Grid Load')
        # # ax.plot(battery_obj.load_down, label='Load Lower Bound')
        # # ax.plot(battery_obj.load_up, label='Load Upper Bound')
        # # ax.plot(battery_obj.load_up, label='Load Prediction')
        # animator = ani.FuncAnimation(fig, p, interval=100)
        # plt.show()
        # plt.cla()

        current_time = current_time + timedelta(seconds=+1)



        ts += 1




    # print("Battery- -> "+str(battery_obj.grid_power_factor))
    # print(battery_obj.grid_original_power_factor)





