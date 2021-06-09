

data = {}
new_battery_setpoint = 0.0
new_grid_load = 0.0
new_grid_reactive_power = 0.0
new_SoC = 0.0
new_battery_reactive_power = 0.0
time_format = '%Y-%m-%d %H:%M:%S'
start_time = gen_config['StartTime']
end_time = gen_config['EndTime']
#gen_config['bat_capacity_kWh'] = ess_capacity
gen_config['rated_kW'] = max_power
gen_config['reserve_soc'] = ess_soc_min_limit/100
battery_obj = battery_class_new(use_case_library, gen_config, data_config)
new_reserve_up_cap = 500 # kW/5 minutes
new_reserve_down_cap = 500 # kW/5 minutes
while ts < simulation_duration:
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
            # check SoC
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
                    # below the complicated 0.5/(5*60) comes from conversion of capacity to power
                    # 0.5 comes from the fact the signal is coming every 2 second, (5*60) because capacity is given for every 5 minutes
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
    # price_temp = new_actual_price
    # print(f"New Battery Setpoint after outage block = {new_battery_setpoint}")
    # print(f"soc actual = {battery_obj.SoC_actual}")
    # print(f"soc prediction = {battery_obj.SoC_prediction}")
    # print(f"grid peak load prediction = {battery_obj.peak_load_prediction}")
    # print(f"grid peak load actual = {max(battery_obj.peak_load_actual)}")
    # print(f"Battery Setpoints Prediction = {battery_obj.battery_setpoints_prediction}")

    # print(f"Battery Setpoints Actual = {battery_obj.battery_setpoints_actual}")
    # print(f"grid load actual 0:ts = {battery_obj.grid_load_actual[0:ts]}")
    # print(f"grid load actual max(0:ts) = {max(battery_obj.grid_load_actual[0:ts])}")

    battery_obj.metrics['peak_surcharge_da'].append(battery_obj.peak_load_prediction * battery_obj.peak_price)
    battery_obj.metrics['original_surcharge'].append(max(battery_obj.peak_load_actual) * battery_obj.peak_price)