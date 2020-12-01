import os
import sys
import json
import numpy as np
from datetime import datetime, timedelta

from battery_class_new import battery_class_new


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



if __name__ == "__main__":

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
                               datetime.strptime(start_time, time_format)).total_seconds())
    current_time = datetime.strptime(start_time, time_format)

    print('simulation start time -> ' + start_time)
    print('simulation end time -> ' + end_time)
    print('simulation duration in seconds -> ' + str(simulation_duration))

    use_case_library = construct_use_case_library(gen_config, control_config)

    print("Use Cases Loaded")


    battery_obj = battery_class_new(use_case_library, gen_config, data_config)

    print("Battery Object Loaded")

    battery_obj.get_data()
    ts = 0

    while ts < simulation_duration:

        # Hourly Optimization Routine
        if ts % 60 == 0:
            print('current time -> ' + str(current_time))
            print("Performing Day-Ahead Optimization")
            current_time = current_time + timedelta(hours=+1)

            interval = timedelta(days=+1)
            forecast_time = current_time + interval

            battery_obj.set_hourly_load_forecast(current_time, forecast_time)


            print("Solving the Day-Ahead Optimization Problem")

            battery_obj.DA_optimal_quantities()

            print("Battery-setpoints (kW) -> "+str(battery_obj.battery_setpoints))
            print("Battery-SoC (kWh)-> "+str(battery_obj.SoC_prediction))
            print("Battery-PeakLoad (kW) -> "+str(battery_obj.peak_load_prediction))
            print("Battery-GridLoad (kW) -> "+str(battery_obj.grid_load_prediction))
            print("Battery-GridReact (kVar) -> "+str(battery_obj.grid_react_power_prediction))
            print("Battery-BattReact (kVar) -> "+str(battery_obj.battery_react_power_prediction))

        # RealTime Control Routine
        # else:
            # print("Performing Real-Time Control")
            # set second by second forecast for next hour
            # use control rules
            # check SoC
            # modify the rules
        ts += 1
    # print("Battery- -> "+str(battery_obj.grid_power_factor))
    # print(battery_obj.grid_original_power_factor)



