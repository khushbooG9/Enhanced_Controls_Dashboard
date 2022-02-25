# Copyright (C) 2017-2019 Battelle Memorial Institute
# file: battery_class_new.py #
"""Class that controls the Battery using DA and RT control Techniques


"""
import math
import numpy as np
from copy import deepcopy
import logging as log
import pyomo.environ as pyo
import pandas as pd
from datetime import datetime, timedelta

class battery_class_new:
    """Class to control battery
    Args:
        TODO: update inputs for this agent

    Attributes: #


    """

    def __init__(self, use_case_dict, gen_dict, data_dict):
        """Initializes the class
        """
        # TODO: update attributes of class
        # initialize from Args:

        self.use_case_dict = use_case_dict
        self.name = gen_dict["batteryName"]

        self.capacity = gen_dict["capacity"]
        self.rating = gen_dict["rating"]
        self.charge = gen_dict["charge"]
        self.efficiency = gen_dict["efficiency"]
        self.StartTime = gen_dict["StartTime"]
        self.EndTime = gen_dict["EndTime"]
        self.SimulationDays = gen_dict["SimulationDays"]
        self.FacilityLoadDataPath = data_dict["FacilityLoadDataPath"]
        self.PriceDataPath = data_dict["PriceDataPath"]
        self.ResPriceDataPath = data_dict["ReservePriceDataPath"]
        self.regSignalDataPath = data_dict["regSignalDataPath"]
        self.rated_inverter_kVA = gen_dict["rated_inverter_kVA"]
        self.rated_kW = gen_dict["rated_kW"]
        self.inv_eta = gen_dict["inv_eta"]
        self.bat_eta = gen_dict["bat_eta"]
        self.rated_kWh = gen_dict["bat_capacity_kWh"]
        self.windowLength = int(gen_dict["windowLength"])

        self.price_dev = gen_dict["price_dev"]
        self.load_dev = gen_dict["load_dev"]
        self.res_price_dev = gen_dict["res_price_dev"]

        self.load_data_resolution = gen_dict["load_data_resolution"]
        self.peak_price = gen_dict["peak_price"]
        self.load_pf = gen_dict["load_pf"]
        self.reserve_SoC = gen_dict["reserve_SoC"]*gen_dict["bat_capacity_kWh"]

        self.TIME = range(0, self.windowLength)
        self.TIME_minus_1 = range(0, self.windowLength-1)
        self.SoC_init = gen_dict["SoC_init"]*gen_dict["bat_capacity_kWh"]

        # demand charge reduction Variables
        self.demand_charge_budget = int(gen_dict["demand_charge_budget"]*self.windowLength)
        self.arbitrage_budget = int(gen_dict["arbitrage_budget"]*self.windowLength)
        self.real_time_control_resolution = gen_dict["real_time_control_resolution"]   # seconds
        self.hrs_to_secs = self.real_time_control_resolution*(1/3600)   # to convert hourly day-ahead results quantities to real-time control time steps

        # Power Factor Correction Variables
        self.lin_segments = int(gen_dict["linearization_segments"])
        self.SEGMENTS = range(1, self.lin_segments+1)
        self.cos_terms = np.cos((np.array(self.SEGMENTS) * np.pi * (1 / self.lin_segments)))
        self.sin_terms = np.sin((np.array(self.SEGMENTS) * np.pi * (1 / self.lin_segments)))
        self.pf_penalty = gen_dict["pf_penalty"]
        self.pf_limit = gen_dict["pf_limit"]
        self.reporting_frequency = gen_dict["reporting_frequency"]

        # reserves placement variable
        self.res_eta_up = gen_dict["res_eta_up"]
        self.res_eta_down = gen_dict["res_eta_down"]
        self.reserve_up_budget = int(gen_dict["reserve_up_budget"]*self.windowLength)
        self.reserve_down_budget = int(gen_dict["reserve_down_budget"]*self.windowLength)
        self.load_data = None
        self.load_predict = None
        self.load_up = None
        self.load_down = None

        self.price_data = None
        self.price_predict = None
        self.price_up = None
        self.price_down = None

        self.res_price_data = None
        self.res_price_predict_up = None
        self.res_price_predict_up_max = None
        self.res_price_predict_up_min = None
        self.res_price_predict_down = None
        self.res_price_predict_down_max = None
        self.res_price_predict_down_min = None
        self.reg_signal_data = None
        self.battery_setpoints_prediction = [[]] * self.windowLength
        self.SoC_prediction = [[]] * self.windowLength
        self.peak_load_prediction = None
        self.grid_load_prediction = [[]] * self.windowLength
        self.grid_react_power_prediction = [[]] * self.windowLength
        self.battery_react_power_prediction = [[]] * self.windowLength
        self.grid_apparent_power_prediction = [[]] * self.windowLength
        self.apparent_power_battery = [[]] * self.windowLength
        self.grid_power_factor_prediction = [[]] * self.windowLength
        self.battery_res_up_prediction = [[]] * self.windowLength
        self.battery_res_down_prediction = [[]] * self.windowLength
        self.arbitrage_revenue_predicted = []
        self.peak_surcharge_predicted = []
        self.reserve_revenue_predicted = []
        self.arbitrage_revenue_actual = []
        self.peak_surcharge_actual = []
        self.reserve_revenue_actual = []

        self.grid_original_apparant_power = [[]] * self.windowLength
        self.grid_original_power_factor = [[]] * self.windowLength

        self.battery_setpoints_actual = []
        self.battery_res_up_cap_actual = []
        self.battery_res_down_cap_actual = []
        self.arbitrage_purchased_power_actual_rt = []
        self.arbitrage_purchased_power_ideal_rt = []
        self.SoC_actual = []
        self.peak_load_actual = []
        self.grid_load_actual = []
        self.grid_react_power_actual = []
        self.battery_react_power_actual = []
        self.actual_load = []
        self.actual_reactive_load = []
        self.grid_apparent_power_actual = []
        self.grid_power_factor_actual = []
        self.actual_price = []
        self.actual_res_price_up = []
        self.actual_res_price_down = []

        self.actual_reg_signal = []

    def change_setpoint(self, old_setpoint, mismatch):
        new_battery_setpoint = min(self.rated_kW, max(-self.rated_kW, old_setpoint + mismatch))

        return new_battery_setpoint

    def check_SoC(self, new_battery_setpoint, current_SoC):
        SoC_temp = current_SoC - new_battery_setpoint * self.hrs_to_secs
        check_SoC = 0
        if SoC_temp < self.reserve_SoC:
            check_SoC = 1
            print("Battery min SoC will violate with this setpoints -- adjusting the power w.r.t. allowable SoC")
            delta_P = (self.reserve_SoC - current_SoC) / self.real_time_control_resolution
            new_battery_setpoint = delta_P
            SoC_temp = self.reserve_SoC

        elif SoC_temp > (self.rated_kWh - self.reserve_SoC):
            check_SoC = 1
            print("Battery max SoC will violate with this setpoints -- adjusting the power w.r.t. allowable SoC")
            delta_P = (self.rated_kWh - self.reserve_SoC - current_SoC) / self.real_time_control_resolution
            new_battery_setpoint = delta_P
            SoC_temp = self.rated_kWh - self.reserve_SoC
        # else:
            # print("New Setpoints satisfy SoC requirement")

        if check_SoC == 1:
            SoC_temp = current_SoC - new_battery_setpoint * self.real_time_control_resolution

        return SoC_temp, new_battery_setpoint

    def rtc_demand_charge_reduction(self, active_power_mismatch, set_point_prediction, current_SoC, actual_load,  batt_react_setpoint, batt_sensitivity):

        new_battery_setpoint = self.change_setpoint(set_point_prediction, batt_sensitivity*active_power_mismatch)

        if np.sqrt(batt_react_setpoint**2 + new_battery_setpoint**2) <= self.rated_inverter_kVA: # new setpoints are within inverter range
            new_SoC, new_battery_setpoint = self.check_SoC(new_battery_setpoint, current_SoC)

            new_grid_load = max(0, actual_load - new_battery_setpoint)
        else:
            print("battery setpoint change has taken the power outside of inverter capacity")
            new_battery_setpoint = np.sqrt(self.rated_inverter_kVA**2 - batt_react_setpoint**2)
            new_battery_setpoint = self.change_setpoint(set_point_prediction, new_battery_setpoint)
            new_SoC, new_battery_setpoint = self.check_SoC(new_battery_setpoint, current_SoC)
            new_grid_load = max(0, actual_load - new_battery_setpoint)

            if new_grid_load == 0:
                # new_battery_setpoints = set_point_prediction
                new_SoC, new_battery_setpoint = self.check_SoC(set_point_prediction, current_SoC)


        return new_SoC, new_battery_setpoint, new_grid_load

    def rtc_power_factor_correction(self, batt_react_power_temp, grid_react_power_temp, reactive_power_mismatch, battery_react_power_ratio, grid_react_power_ratio,  grid_act_power_temp):
        new_battery_reactive_power = batt_react_power_temp + battery_react_power_ratio * reactive_power_mismatch
        new_grid_reactive_power = grid_react_power_temp + grid_react_power_ratio * reactive_power_mismatch
        apparant_temp = self.get_apparent_power(grid_act_power_temp, new_grid_reactive_power)
        pf_temp = self.get_power_factor(grid_act_power_temp, apparant_temp)


        return new_battery_reactive_power, new_grid_reactive_power, apparant_temp, pf_temp


    def get_data(self):
        """ loads data in the module
        load data
        price data

         Args:
             forecasted_price (float x 48): cleared price in $/kWh
         """
        self.load_data = pd.read_csv(self.FacilityLoadDataPath)
        self.load_data['Time'] = pd.to_datetime(self.load_data['Time'].values)
        self.load_data.set_index('Time')

        # self.load_data = self.load_data[
        #     (self.load_data['Time'] >= self.StartTime) & (self.load_data['Time'] < self.EndTime)]
        if len(self.load_data['Time']) == 0:
            print("load data is not in the StartTime and EndTime range")
        if len(self.load_data['Time']) < self.windowLength*365:
            print("load data is not for the whole year")

        self.price_data = pd.read_csv(self.PriceDataPath)
        # multiply by 1e-3 to convert $/MWh to $/MVarh
        self.price_data['Value'] = self.price_data['Value'] * 1e-3
        self.price_data['Time'] = pd.to_datetime(self.price_data['Time'].values)
        self.price_data.set_index('Time')

        # self.load_data = self.load_data[
        #     (self.load_data['Time'] >= self.StartTime) & (self.load_data['Time'] < self.EndTime)]
        if len(self.price_data['Time']) == 0:
            print("load data is not in the StartTime and EndTime range")
        if len(self.price_data['Time']) < self.windowLength * 365:
            print("load data is not for the whole year")

        self.res_price_data = pd.read_csv(self.ResPriceDataPath)
        self.res_price_data['Value'] = self.res_price_data['Value'] * 1e-3
        self.res_price_data['Time'] = pd.to_datetime(self.res_price_data['Time'].values)
        self.res_price_data.set_index('Time')

        # self.load_data = self.load_data[
        #     (self.load_data['Time'] >= self.StartTime) & (self.load_data['Time'] < self.EndTime)]
        if len(self.res_price_data['Time']) == 0:
            print("load data is not in the StartTime and EndTime range")
        if len(self.res_price_data['Time']) < self.windowLength * 365:
            print("load data is not for the whole year")

        self.reg_signal_data = pd.read_csv(self.regSignalDataPath)
        self.reg_signal_data['Time'] = pd.to_datetime(self.reg_signal_data['Time'].values)
        self.reg_signal_data['Time'] = self.reg_signal_data.Time.dt.strftime('%H:%M:%S')
        # self.reg_signal_data['Hour'] =  self.reg_signal_data.Time.dt.hour
        # self.reg_signal_data['Minute'] = self.reg_signal_data.Time.dt.minute
        # self.reg_signal_data['Second'] = self.reg_signal_data.Time.dt.second
        self.reg_signal_data.set_index('Time')

    def set_hourly_load_forecast(self, current_time, forecast_time, ts):
        """ Set the f_DA attribute

        Args:
            Forecasted Load (float x 48): in kW, kVar
        """
        self.load_predict = self.load_data[(self.load_data['Time'] >= current_time) & (self.load_data['Time'] < forecast_time)]['Value'].values
        if ts > 0:
            self.load_predict[0] = self.actual_load[ts-1]
        self.load_up = self.load_predict + self.load_predict*self.load_dev
        self.load_down = self.load_predict - self.load_predict*self.load_dev
        # self.load_predict = self.load_predict + (self.load_dev*np.random.rand(len(self.load_predict))*self.load_up)-(self.load_dev*np.random.rand(len(self.load_predict))*self.load_down)
        # because we know the forecast at the current time step
        # if ts > 0:
        #     self.load_predict[0] = self.actual_load[ts-1]
        #
        # self.load_up[0] = self.load_predict[0]
        # self.load_down[0] = self.load_predict[0]
        self.grid_original_apparant_power = np.sqrt(self.load_predict**2 + (self.load_pf*self.load_predict)**2)
        self.grid_original_power_factor = (self.load_predict+1e-4)/(self.grid_original_apparant_power+1e-4)


    def set_load_actual(self, load_val, diff):
        dev = ((self.load_dev*np.random.randn(1)[0]*0.3)-(self.load_dev*np.random.randn(1)[0]*0.3))
        # dev = 0.0
        self.actual_load.append(load_val + diff + dev)
        self.actual_reactive_load.append( (load_val + diff + dev)*self.load_pf)

    def set_hourly_price_forecast(self, current_time, forecast_time, ts):
        """ Set the forecast price

        Args:
            Forecasted Price (float x 24): in $/kWh
        """
        self.price_predict = self.price_data[(self.price_data['Time'] >= current_time) & (self.price_data['Time'] < forecast_time)]['Value'].values
        self.price_up = self.price_predict + self.price_predict*self.price_dev
        self.price_down = self.price_predict - self.price_predict*self.price_dev
        self.price_up[0] = self.price_predict[0]
        self.price_down[0] = self.price_predict[0]

    def set_hourly_res_price_forecast(self, current_time, forecast_time, ts):
        """ Set the forecast price

        Args:
            Forecasted Price (float x 24): in $/kWh
        """
        self.res_price_predict = self.res_price_data[(self.res_price_data['Time'] >= current_time) & (self.res_price_data['Time'] < forecast_time)]['Value'].values
        self.res_price_predict_up = self.res_price_predict + abs(np.mean(self.res_price_predict)*(np.random.randn(len(self.res_price_predict)) - np.random.randn(len(self.res_price_predict))))
        self.res_price_predict_down = self.res_price_predict + abs(np.mean(self.res_price_predict)*(np.random.randn(len(self.res_price_predict)) - np.random.randn(len(self.res_price_predict))))

        self.res_price_predict_up_max = self.res_price_predict_up + self.res_price_predict_up*self.res_price_dev
        self.res_price_predict_up_min = self.res_price_predict_up - self.res_price_predict_up*self.res_price_dev
        self.res_price_predict_up_max[0] = self.res_price_predict_up[0]
        self.res_price_predict_up_min[0] = self.res_price_predict_up[0]

        self.res_price_predict_down_max = self.res_price_predict_down + self.res_price_predict_down*self.res_price_dev
        self.res_price_predict_down_min = self.res_price_predict_down - self.res_price_predict_down*self.res_price_dev
        self.res_price_predict_down_max[0] = self.res_price_predict_down[0]
        self.res_price_predict_down_min[0] = self.res_price_predict_down[0]

    def set_price_actual(self, price_val, diff, ts):
        if (ts%300) == 0:
            dev = 0.025*(price_val*np.random.randn(1)[0] - price_val*np.random.randn(1)[0])
        else:
            dev = 0.0
            diff = 0.0
        self.actual_price.append(price_val + dev + diff)

    def set_res_price_actual(self, price_val_up, price_val_down, diff1, diff2, ts):
        if (ts%300) == 0:
            dev1 = 0.025*(price_val_up*np.random.randn(1)[0] - price_val_up*np.random.randn(1)[0])
            dev2 = 0.025*(price_val_down*np.random.randn(1)[0] - price_val_down*np.random.randn(1)[0])

        else:
            dev1 = 0.0
            diff1 = 0.0
            dev2 = 0.0
            diff2 = 0.0
        self.actual_res_price_up.append(price_val_up + dev1 + diff1)
        self.actual_res_price_down.append(price_val_down + dev2 + diff2)

    def get_reg_signal(self, current_time, ts):
        t = current_time.strftime('%H:%M:%S')
        # forecast_time = timedelta(seconds=+4)
        # self.reg_signal_data.loc[(self.reg_signal_data['Hour'] == 0) & ((self.reg_signal_data['Minute'] == 0)) & (
        # (self.reg_signal_data['Second'] == 0))]
        try:
            self.actual_reg_signal.append(self.reg_signal_data[(self.reg_signal_data['Time'] == t)]['Value'].values[0])
            # self.actual_reg_signal.append(self.reg_signal_data[(self.reg_signal_data['Time'] >= t) & (self.reg_signal_data['Time'] < t)]['Value'].values)
        except:
            self.actual_reg_signal.append(self.actual_reg_signal[ts-1])

    def set_SoC(self, latest_SoC):
        self.SoC_init = latest_SoC

    def get_apparent_power(self, p, q):
        apparent_power = np.sqrt(p**2 + q**2)
        return apparent_power

    def get_power_factor(self, p,s):
        pf = (abs(p)+1e-6)/(s+1e-6)
        return pf

    def obj_rule(self, m):
        temp = 0
        if self.use_case_dict["power_factor_correction"]["control_type"] == "opti-based":
            temp = temp + sum(m.theta[i] for i in self.TIME)

        if self.use_case_dict["demand_charge"]["control_type"] == "opti-based":
            temp = temp + sum(m.eta_D[i] for i in self.TIME) + self.peak_price*m.p_peak + self.demand_charge_budget*m.beta_D

        if self.use_case_dict["energy_arbitrage"]["control_type"] == "opti-based":
            temp = temp + sum(m.eta_A[i] for i in self.TIME_minus_1) \
                   + sum(self.price_down[i+1]*(m.p_chg[i+1]-m.p_dis[i+1]) for i in self.TIME_minus_1) \
                   + self.arbitrage_budget*m.beta_A
            temp = temp + self.price_predict[0]*(m.p_chg[0]-m.p_dis[0])

        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            temp = temp + sum(m.eta_R_up[i] for i in self.TIME_minus_1) \
                   - sum(self.res_price_predict_up_min[i+1]*(m.p_reg_up[i+1]) for i in self.TIME_minus_1) \
                   + self.reserve_up_budget*m.beta_R_up\
                   + sum(m.eta_R_down[i] for i in self.TIME_minus_1) \
                   - sum(self.res_price_predict_down_min[i + 1] * (m.p_reg_down[i + 1]) for i in self.TIME_minus_1) \
                   + self.reserve_down_budget * m.beta_R_down

            temp = temp - self.res_price_predict_up[0]*m.p_reg_up[0] - self.res_price_predict_down[0]*m.p_reg_down[0]

        return temp


    def con_rule_ine1_demand_chg(self, m, i):
        if self.use_case_dict["demand_charge"]["control_type"] == "opti-based":
            return m.beta_D + m.eta_D[i] >= (self.load_up[i] - self.load_down[i])
        else:
            return m.beta_D + m.eta_D[i] == 0.0

    def con_rule_ine1_arbitrage(self, m, i):
        if self.use_case_dict["energy_arbitrage"]["control_type"] == "opti-based":
            return m.beta_A + m.eta_A[i] >= (self.price_up[i+1] - self.price_down[i+1])*m.p_chg[i+1]
        else:
            return m.beta_A + m.eta_A[i] == 0.0

    def con_rule_ine1_reg_up(self, m, i):
        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            return m.p_reg_up[i] <= (self.rated_kW - (self.rated_kW*(self.reserve_SoC/self.rated_kWh))) - (m.p_dis[i] - m.p_chg[i])
        else:
            return m.p_reg_up[i] == 0.0

    def con_rule_ine1_reg_down(self, m, i):
        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            return m.p_reg_down[i] <= (self.rated_kW - (self.rated_kW*(self.reserve_SoC/self.rated_kWh))) + (m.p_dis[i] - m.p_chg[i])
        else:
            return m.p_reg_down[i] == 0.0

    def con_rule_ine21_reg_up(self, m, i):
        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            return m.SoC[i] - (self.res_eta_up*m.p_reg_up[i]/self.bat_eta) <= (self.rated_kWh-self.reserve_SoC)
        else:
            return m.p_reg_up[i] == 0.0

    def con_rule_ine22_reg_up(self, m, i):
        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            return self.reserve_SoC <= m.SoC[i] - (self.res_eta_up*m.p_reg_up[i]/self.bat_eta)
        else:
            return m.p_reg_up[i] == 0.0

    def con_rule_ine21_reg_down(self, m, i):
        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            return m.SoC[i] + (self.res_eta_down*m.p_reg_down[i]*self.bat_eta) <= (self.rated_kWh-self.reserve_SoC)

        else:
            return m.p_reg_down[i] == 0.0

    def con_rule_ine22_reg_down(self, m, i):
        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            return self.reserve_SoC <= m.SoC[i] + (self.res_eta_down*m.p_reg_down[i]*self.bat_eta)

        else:
            return m.p_reg_down[i] == 0.0


    def con_rule_ine3_reg_up(self, m, i):
        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            return m.beta_R_up + m.eta_R_up[i] >= (self.res_price_predict_up_max[i+1] - self.res_price_predict_up_min[i+1])*m.p_reg_up[i+1]
        else:
            return m.beta_R_up + m.eta_R_up[i] == 0

    def con_rule_ine3_reg_down(self, m, i):
        if self.use_case_dict["reserves_placement"]["control_type"] == "opti-based":
            return m.beta_R_down + m.eta_R_down[i] >= (
                        self.res_price_predict_down_max[i+1] - self.res_price_predict_down_min[i+1]) * m.p_reg_down[i+1]
        else:
            return m.beta_R_down + m.eta_R_down[i] == 0


    def con_rule_ine2_demand_chg(self, m, i):
        if self.use_case_dict["demand_charge"]["control_type"] == "opti-based":
            return m.p_total[i] + m.eta_D[i] <= m.p_peak
        else:
            return m.p_total[i] <= m.p_peak

    def con_rule_ine3_inverter(self, m, i, k):
        if self.use_case_dict["power_factor_correction"]["control_type"] == "opti-based":
            return m.p_batt[i]*self.cos_terms[k-1] + m.q_batt[i]*self.sin_terms[k-1] <= self.rated_inverter_kVA
        else:
            return m.q_batt[i] == 0.0

    def con_rule_ine4_inverter(self, m, i, k):
        if self.use_case_dict["power_factor_correction"]["control_type"] == "opti-based":
            return m.p_batt[i]*self.cos_terms[k-1] + m.q_batt[i]*self.sin_terms[k-1] >= -self.rated_inverter_kVA
        else:
            return m.q_batt[i] == 0.0

    def con_rule_ine5_pcc(self, m, i, k):
        if self.use_case_dict["power_factor_correction"]["control_type"] == "opti-based":
            return self.pf_limit*(m.p_total[i]*self.cos_terms[k-1] + m.q_total[i]*self.sin_terms[k-1])*self.pf_penalty\
                   <= m.theta[i]-m.p_total[i]*self.pf_penalty
        else:
            return m.q_batt[i] == 0.0
    def con_rule_ine6_pcc(self, m, i, k):
        if self.use_case_dict["power_factor_correction"]["control_type"] == "opti-based":
            return self.pf_limit*(m.p_total[i]*self.cos_terms[k-1] + m.q_total[i]*self.sin_terms[k-1])*self.pf_penalty\
                   >= m.p_total[i]*self.pf_penalty - m.theta[i]
        else:
            return m.q_batt[i] == 0.0

    def con_rule_eq4_q_balance(self, m, i):
        return m.q_total[i] == self.load_pf*m.p_total[i] + m.q_batt[i]

    def con_rule_eq1_chg_dis(self, m, i):
        if self.use_case_dict["demand_charge"]["control_type"] == "opti-based":
            return m.p_batt[i] == -self.bat_eta*m.p_chg[i] + (1/self.bat_eta)*(m.p_dis[i] + m.eta_D[i])
        else:
            return m.p_batt[i] == -self.bat_eta*m.p_chg[i] + (1/self.bat_eta)*(m.p_dis[i])

    def con_rule_eq2_p_balance(self, m, i):
        return m.p_total[i] == -m.p_batt[i] + self.load_up[i]

    def con_rule_eq3_soc(self, m, i):
        if self.SoC_init < self.reserve_SoC:
            self.SoC_init = self.reserve_SoC
        elif self.SoC_init > (self.rated_kWh-self.reserve_SoC):
            self.SoC_init = (self.rated_kWh-self.reserve_SoC)

        if i == 0:
            return m.SoC[i] == self.SoC_init - m.p_batt[i]
        else:
            return m.SoC[i] == m.SoC[i-1] - m.p_batt[i]


    def con_rule_eq31_soc_term(self, m, i):
        if i == 23:
            return m.SoC[i] >= (self.rated_kWh-self.reserve_SoC)/2
        else:
            return pyo.Constraint.Skip
    def DA_optimal_quantities(self):
        """ Generates Day Ahead optimized quantities for Battery

        Returns:
            Quantity (float) (1 x windowLength): Optimal quantity from optimization for all hours of the window specified by windowLength
        """

        model = pyo.ConcreteModel()
        model.p_dis = pyo.Var(self.TIME, bounds=(0, self.rated_kW))
        model.p_chg = pyo.Var(self.TIME, bounds=(0, self.rated_kW))
        model.p_peak = pyo.Var(bounds=(0, None))
        model.p_reg_up = pyo.Var(self.TIME, bounds=(0, self.rated_kW - (self.rated_kW*(self.reserve_SoC/self.rated_kWh))))
        model.p_reg_down = pyo.Var(self.TIME, bounds=(0, self.rated_kW - (self.rated_kW*(self.reserve_SoC/self.rated_kWh))))
        model.p_batt = pyo.Var(self.TIME)
        model.q_batt = pyo.Var(self.TIME)

        model.p_total = pyo.Var(self.TIME, bounds=(0, None))
        model.q_total = pyo.Var(self.TIME)

        model.SoC = pyo.Var(self.TIME, bounds=(self.reserve_SoC, self.rated_kWh-self.reserve_SoC))

        model.eta_D = pyo.Var(self.TIME, bounds=(0, None))
        model.beta_D = pyo.Var(bounds = (0, None))

        model.eta_A = pyo.Var(self.TIME_minus_1, bounds=(0, None))
        model.beta_A = pyo.Var(bounds = (0, None))

        model.eta_R_down = pyo.Var(self.TIME_minus_1, bounds=(0, None))
        model.eta_R_up = pyo.Var(self.TIME_minus_1, bounds=(0, None))

        model.beta_R_down = pyo.Var(bounds = (0, None))
        model.beta_R_up = pyo.Var(bounds = (0, None))

        model.theta = pyo.Var(self.TIME, bounds = (0, None))

        model.con1 = pyo.Constraint(self.TIME, rule=self.con_rule_ine1_demand_chg)
        model.con2 = pyo.Constraint(self.TIME, rule=self.con_rule_ine2_demand_chg)

        model.con3 = pyo.Constraint(self.TIME, self.SEGMENTS, rule=self.con_rule_ine3_inverter)
        model.con4 = pyo.Constraint(self.TIME, self.SEGMENTS, rule=self.con_rule_ine4_inverter)
        model.con5 = pyo.Constraint(self.TIME, self.SEGMENTS, rule=self.con_rule_ine5_pcc)
        model.con6 = pyo.Constraint(self.TIME, self.SEGMENTS, rule=self.con_rule_ine6_pcc)

        model.con7 = pyo.Constraint(self.TIME, rule=self.con_rule_eq1_chg_dis)
        model.con8 = pyo.Constraint(self.TIME, rule=self.con_rule_eq2_p_balance)
        model.con9 = pyo.Constraint(self.TIME, rule=self.con_rule_eq3_soc)
        model.con10 = pyo.Constraint(self.TIME, rule=self.con_rule_eq4_q_balance)
        model.con11 = pyo.Constraint(self.TIME_minus_1, rule=self.con_rule_ine1_arbitrage)
        model.con12 = pyo.Constraint(self.TIME, rule=self.con_rule_ine1_reg_up)
        model.con13 = pyo.Constraint(self.TIME, rule=self.con_rule_ine21_reg_up)
        model.con14 = pyo.Constraint(self.TIME, rule=self.con_rule_ine22_reg_up)
        model.con15 = pyo.Constraint(self.TIME_minus_1, rule=self.con_rule_ine3_reg_up)
        model.con16 = pyo.Constraint(self.TIME, rule=self.con_rule_ine1_reg_down)
        model.con17 = pyo.Constraint(self.TIME, rule=self.con_rule_ine21_reg_down)
        model.con18 = pyo.Constraint(self.TIME, rule=self.con_rule_ine22_reg_down)
        model.con19 = pyo.Constraint(self.TIME_minus_1, rule=self.con_rule_ine3_reg_down)

        model.con20 = pyo.Constraint(self.TIME, rule=self.con_rule_eq31_soc_term)

        model.obj = pyo.Objective(rule=self.obj_rule, sense=pyo.minimize)

        pyo.SolverFactory('ipopt').solve(model)  # solver being used


        # p_chg_val = [0] * len(self.TIME)
        # p_dis_val = [0] * len(self.TIME)
        # soc_val = [0] * len(self.TIME)
        # p_batt_val = [0] * len(self.TIME)
        # p_total_val = [0] * len(self.TIME)
        #         self.grid_react_power_prediction = [[]] * self.windowLength
        #         self.battery_react_power_prediction = [[]] * self.windowLength
        #     battery_obj.grid_power_factor
        try:
            self.battery_setpoints_prediction = [[]] * self.windowLength
            self.SoC_prediction = [[]] * self.windowLength
            self.grid_load_prediction = [[]] * self.windowLength
            # TOL = 0.00001  # Tolerance for checking bid
            for t in self.TIME:
                # if pyo.value(model.p_chg[t]) > TOL:
                #     p_chg_val[t] = pyo.value(model.p_chg[t])  # For logging
                # if pyo.value(model.E_DA_out[t]) > TOL:
                #     p_dis_val[t] = pyo.value(model.p_dis[t])
                self.SoC_prediction[t] = pyo.value(model.SoC[t])
                self.battery_setpoints_prediction[t] = pyo.value(model.p_batt[t])
                self.grid_load_prediction[t] = pyo.value(model.p_total[t])
                self.grid_react_power_prediction[t] = pyo.value(model.q_total[t])
                self.battery_react_power_prediction[t] = pyo.value(model.q_batt[t])
                self.battery_res_up_prediction[t] = pyo.value(model.p_reg_up[t]*self.res_eta_up)
                self.battery_res_down_prediction[t] = pyo.value(model.p_reg_down[t]*self.res_eta_down)
                self.grid_apparent_power_prediction[t] = self.get_apparent_power(self.grid_load_prediction[t], self.grid_react_power_prediction[t])
                self.grid_power_factor_prediction[t] = self.get_power_factor(self.grid_load_prediction[t], self.grid_apparent_power_prediction[t])
            self.peak_load_prediction = pyo.value(model.p_peak)
        except:
            print('Optimization Failed')



if __name__ == "__main__":
    """Testing

    Makes a single battery agent and run DA 
    """


