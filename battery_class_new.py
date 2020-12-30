# Copyright (C) 2017-2019 Battelle Memorial Institute
# file: battery_dsot_v1.py # TODO: update
"""Class that controls the Battery


"""
import math
import numpy as np
import tesp_support.helpers as helpers
from copy import deepcopy
import logging as log
import pyomo.environ as pyo
import pandas as pd
import json
import matplotlib.pyplot as plt

class battery_class_new:
    """Class to control battery

    Args:
        TODO: update inputs for this agent

    Attributes: #TODO: update attributes for this agent


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
        self.rated_inverter_kVA = gen_dict["rated_inverter_kVA"]
        self.rated_kW = gen_dict["rated_kW"]
        self.inv_eta = gen_dict["inv_eta"]
        self.bat_eta = gen_dict["bat_eta"]
        self.rated_kWh = gen_dict["bat_capacity_kWh"]
        self.windowLength = int(gen_dict["windowLength"])
        self.price_dev = gen_dict["price_dev"]
        self.load_dev = gen_dict["load_dev"]
        self.load_data_resolution = gen_dict["load_data_resolution"]
        self.peak_price = gen_dict["peak_price"]
        self.load_pf = gen_dict["load_pf"]
        self.reserve_SoC = gen_dict["reserve_SoC"]*gen_dict["bat_capacity_kWh"]

        self.TIME = range(0, self.windowLength)
        self.SoC_init = gen_dict["SoC_init"]*gen_dict["bat_capacity_kWh"]

        # demand charge reduction Variables
        self.demand_charge_budget = int(gen_dict["demand_charge_budget"]*self.windowLength)

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

        self.load_data = None
        self.load_predict = None
        self.load_up = None
        self.load_down = None
        self.price_data = None


        self.battery_setpoints_prediction = [[]] * self.windowLength
        self.SoC_prediction = [[]] * self.windowLength
        self.peak_load_prediction = None
        self.grid_load_prediction = [[]] * self.windowLength

        self.grid_react_power_prediction = [[]] * self.windowLength
        self.battery_react_power_prediction = [[]] * self.windowLength

        self.grid_apparent_power_prediction = [[]] * self.windowLength
        self.apparent_power_battery = [[]] * self.windowLength

        self.grid_power_factor_prediction = [[]] * self.windowLength

        self.grid_original_apparant_power = [[]] * self.windowLength
        self.grid_original_power_factor = [[]] * self.windowLength

        self.battery_setpoints_actual = []
        self.SoC_actual = []
        self.peak_load_actual = []
        self.grid_load_actual = []
        self.grid_react_power_actual = []
        self.battery_react_power_actual = []
        self.actual_load = []
        self.grid_apparent_power_actual = []
        self.grid_power_factor_actual = []

    def todict(self):
        data = {}
        # data["name"] = self.name
        # data["capacity"] = self.capacity
        # data["rating"] = self.rating
        # data["charge"] = self.charge
        # data["efficiency"] = self.efficiency
        # data["StartTime"] = self.StartTime
        # data["EndTime"] = self.EndTime
        # data["SimulationDays"] = self.SimulationDays
        # data["FacilityLoadDataPath"] = self.FacilityLoadDataPath
        # data["PriceDataPath"] = self.PriceDataPath
        # data["rated_inverter_kVA"] = self.rated_inverter_kVA
        # data["rated_kW"] = self.rated_kW
        # data["inv_eta"]  = self.inv_eta
        # data["bat_eta"] = self.bat_eta
        # data["rated_kWh"] = self.rated_kWh
        # data["windowLength"] = self.windowLength
        # data["price_dev"] = self.price_dev
        # data["load_dev"] = self.load_dev
        # data["load_data_resolution"] = self.load_data_resolution
        # data["peak_price"] = self.peak_price
        # data["load_pf"] = self.load_pf
        # data["reserve_SoC"] = self.reserve_SoC
        data["TIME"] = list(self.TIME)
        data["SoC_init"] = self.SoC_init
        data["demand_charge_budget"] = self.demand_charge_budget
        data["real_time_control_resolution"] = self.real_time_control_resolution
        data["hrs_to_secs"] = self.hrs_to_secs
        data["lin_segments"] = self.lin_segments
        data["SEGMENTS"] = list(self.SEGMENTS)
        data["cos_terms"] = self.cos_terms
        data["sin_terms"] = self.sin_terms
        data["pf_penalty"] = self.pf_penalty
        data["pf_limit"] = self.pf_limit
        data["reporting_frequency"] = self.reporting_frequency
        data["load_data"] = self.load_data.to_json()
        data["load_predict"] = self.load_predict
        data["load_up"] = self.load_up
        data["load_down"] = self.load_down
        data["price_data"] = self.price_data.to_json()
        data["battery_setpoints_prediction"] = self.battery_setpoints_prediction
        data["SoC_prediction"] = self.SoC_prediction
        data["peak_load_prediction"] = self.peak_load_prediction
        data["grid_load_prediction"] = self.grid_load_prediction
        data["grid_react_power_prediction"] = self.grid_react_power_prediction
        data["battery_react_power_prediction"] = self.battery_react_power_prediction
        data["grid_apparent_power_prediction"] = self.grid_apparent_power_prediction
        data["apparent_power_battery"] = self.apparent_power_battery
        data["grid_power_factor_prediction"] = self.grid_power_factor_prediction
        data["grid_original_apparant_power"] = self.grid_original_apparant_power
        data["grid_original_power_factor"] = self.grid_original_power_factor
        data["battery_setpoints_actual"] = self.battery_setpoints_actual
        data["SoC_actual"] = self.SoC_actual
        data["peak_load_actual"] = self.peak_load_actual
        data["grid_load_actual"] = self.grid_load_actual
        data["grid_react_power_actual"] = self.grid_react_power_actual
        data["battery_react_power_actual"] = self.battery_react_power_actual
        data["actual_load"] = self.actual_load
        data["grid_apparent_power_actual"] = self.grid_apparent_power_actual
        data["grid_power_factor_actual"] = self.grid_power_factor_actual
        
        return data 


    def fromdict(self, data):
        # self.use_case_dict = data["use_case_dict"]
        # self.name = data["name"]
        # self.capacity = data["capacity"]
        # self.rating = data["rating"]
        # self.charge = data["charge"]
        # self.efficiency = data["efficiency"]
        # self.StartTime = data["StartTime"]
        # self.EndTime = data["EndTime"]
        # self.SimulationDays = data["SimulationDays"]
        # self.FacilityLoadDataPath = data["FacilityLoadDataPath"]
        # self.PriceDataPath = data["PriceDataPath"]
        # self.rated_inverter_kVA = data["rated_inverter_kVA"]
        # self.rated_kW = data["rated_kW"]
        # self.inv_eta = data["inv_eta"]
        # self.bat_eta = data["bat_eta"]
        # self.rated_kWh = data["rated_kWh"]
        # self.windowLength = data["windowLength"]
        # self.price_dev = data["price_dev"]
        # self.load_dev = data["load_dev"]
        # self.load_data_resolution = data["load_data_resolution"]
        # self.peak_price = data["peak_price"]
        # self.load_pf = data["load_pf"]
        # self.reserve_SoC = data["reserve_SoC"]

        self.TIME = data["TIME"]
        self.SoC_init = data["SoC_init"]

        # demand charge reduction Variables
        self.demand_charge_budget = data["demand_charge_budget"]

        self.real_time_control_resolution = data["real_time_control_resolution"] # seconds
        self.hrs_to_secs = data["hrs_to_secs"]  # to convert hourly day-ahead results quantities to real-time control time steps

        # Power Factor Correction Variables
        self.lin_segments = data["lin_segments"]
        self.SEGMENTS = data["SEGMENTS"]
        self.cos_terms = data["cos_terms"]
        self.sin_terms = data["sin_terms"]
        self.pf_penalty = data["pf_penalty"]
        self.pf_limit = data["pf_limit"]
        self.reporting_frequency = data["reporting_frequency"]

        self.load_data = pd.read_json(data["load_data"])
        self.load_predict = data["load_predict"]
        self.load_up = data["load_up"]
        self.load_down = data["load_down"]
        self.price_data = pd.read_json(data["price_data"])


        self.battery_setpoints_prediction = data["battery_setpoints_prediction"]
        self.SoC_prediction = data["SoC_prediction"]
        self.peak_load_prediction = data["peak_load_prediction"]
        self.grid_load_prediction = data["grid_load_prediction"]

        self.grid_react_power_prediction = data["grid_react_power_prediction"]
        self.battery_react_power_prediction = data["battery_react_power_prediction"]

        self.grid_apparent_power_prediction = data["grid_apparent_power_prediction"]
        self.apparent_power_battery = data["apparent_power_battery"]

        self.grid_power_factor_prediction = data["grid_power_factor_prediction"]

        self.grid_original_apparant_power = data["grid_original_apparant_power"]
        self.grid_original_power_factor = data["grid_original_power_factor"]

        self.battery_setpoints_actual = data["battery_setpoints_actual"]
        self.SoC_actual = data["SoC_actual"]
        self.peak_load_actual = data["peak_load_actual"]
        self.grid_load_actual = data["grid_load_actual"]
        self.grid_react_power_actual = data["grid_react_power_actual"]
        self.battery_react_power_actual = data["battery_react_power_actual"]
        self.actual_load = data["actual_load"]
        self.grid_apparent_power_actual = data["grid_apparent_power_actual"]
        self.grid_power_factor_actual = data["grid_power_factor_actual"]


    def copydata(self, other):
        self.use_case_dict = other.use_case_dict
        self.name = other.name
        self.capacity = other.capacity
        self.rating = other.rating
        self.charge = other.charge
        self.efficiency = other.efficiency
        self.StartTime = other.StartTime
        self.EndTime = other.EndTime
        self.SimulationDays = other.SimulationDays
        self.FacilityLoadDataPath = other.FacilityLoadDataPath
        self.PriceDataPath = other.PriceDataPath
        self.rated_inverter_kVA = other.rated_inverter_kVA
        self.rated_kW = other.rated_kW
        self.inv_eta = other.inv_eta
        self.bat_eta = other.bat_eta
        self.rated_kWh = other.rated_kWh
        self.windowLength = other.windowLength
        self.price_dev = other.price_dev
        self.load_dev = other.load_dev
        self.load_data_resolution = other.load_data_resolution
        self.peak_price = other.peak_price
        self.load_pf = other.load_pf
        self.reserve_SoC = other.reserve_SoC

        self.TIME = other.TIME
        self.SoC_init = other.SoC_init

        # demand charge reduction Variables
        self.demand_charge_budget = other.demand_charge_budget

        self.real_time_control_resolution = other.real_time_control_resolution  # seconds
        self.hrs_to_secs = other.hrs_to_secs   # to convert hourly day-ahead results quantities to real-time control time steps

        # Power Factor Correction Variables
        self.lin_segments = other.lin_segments
        self.SEGMENTS = other.SEGMENTS
        self.cos_terms = other.cos_terms
        self.sin_terms = other.sin_terms
        self.pf_penalty = other.pf_penalty
        self.pf_limit = other.pf_limit
        self.reporting_frequency = other.reporting_frequency

        self.load_data = other.load_data
        self.load_predict = other.load_predict
        self.load_up = other.load_up
        self.load_down = other.load_down
        self.price_data = other.price_data


        self.battery_setpoints_prediction = other.battery_setpoints_prediction
        self.SoC_prediction = other.SoC_prediction
        self.peak_load_prediction = other.peak_load_prediction
        self.grid_load_prediction = other.grid_load_prediction

        self.grid_react_power_prediction = other.grid_react_power_prediction
        self.battery_react_power_prediction = other.battery_react_power_prediction

        self.grid_apparent_power_prediction = other.grid_apparent_power_prediction
        self.apparent_power_battery = other.apparent_power_battery

        self.grid_power_factor_prediction = other.grid_power_factor_prediction

        self.grid_original_apparant_power = other.grid_original_apparant_power
        self.grid_original_power_factor = other.grid_original_power_factor

        self.battery_setpoints_actual = other.battery_setpoints_actual
        self.SoC_actual = other.SoC_actual
        self.peak_load_actual = other.peak_load_actual
        self.grid_load_actual = other.grid_load_actual
        self.grid_react_power_actual = other.grid_react_power_actual
        self.battery_react_power_actual = other.battery_react_power_actual
        self.actual_load = other.actual_load
        self.grid_apparent_power_actual = other.grid_apparent_power_actual
        self.grid_power_factor_actual = other.grid_power_factor_actual

    def change_setpoint(self, old_setpoint, mismatch):
        new_battery_setpoint = min(self.rated_kW, max(-self.rated_kW, old_setpoint + mismatch))

        return new_battery_setpoint

    def check_SoC(self, new_battery_setpoint, current_SoC):
        SoC_temp = current_SoC - new_battery_setpoint * self.hrs_to_secs
        check_SoC = 0
        if SoC_temp < self.reserve_SoC:
            check_SoC = 1
            #print("Battery min SoC will violate with this setpoints -- adjusting the power w.r.t. allowable SoC")
            delta_P = (self.reserve_SoC - current_SoC) / self.real_time_control_resolution
            new_battery_setpoint = delta_P
            SoC_temp = self.reserve_SoC

        elif SoC_temp > (self.rated_kWh - self.reserve_SoC):
            check_SoC = 1
            #print("Battery max SoC will violate with this setpoints -- adjusting the power w.r.t. allowable SoC")
            delta_P = (self.rated_kWh - self.reserve_SoC - current_SoC) / self.real_time_control_resolution
            new_battery_setpoint = delta_P
            SoC_temp = self.rated_kWh - self.reserve_SoC
        else:
            pass
            #print("New Setpoints satisfy SoC requirement")

        if check_SoC == 1:
            SoC_temp = current_SoC - new_battery_setpoint * self.real_time_control_resolution

        return SoC_temp, new_battery_setpoint

    def rtc_demand_charge_reduction(self, i, active_power_mismatch, set_point_prediction, current_SoC, actual_load):
        if i == 0:  # highest priority
            #print("Demand Charge is the highest priority")
            if active_power_mismatch > 0.0:
                #print("positive Mismatch Found --> battery should discharge")
                # adjust battery power setpoint and see whether the adjusted power is even physically possible
                new_battery_setpoint = self.change_setpoint(set_point_prediction, active_power_mismatch)
                # check SoC
                new_SoC, new_battery_setpoint = self.check_SoC(new_battery_setpoint, current_SoC)
                # new grid load
                new_grid_load = actual_load - new_battery_setpoint

                # check grid loading

                # if new_grid_load > self.peak_load_prediction:
                #     # print(
                #     #     "new grid load has become higher than peak load --> either mismatch is too big or SoC limits have reached")
                # else:
                #     print("adjusted battery power and kept the peak load as planned")

            else:
                # print(
                #     "negative_mismatch Found --> actual load is less than predicted, so keep the setpoints as is")
                new_grid_load = actual_load + active_power_mismatch - set_point_prediction
                new_battery_setpoint = set_point_prediction
                new_SoC, new_battery_setpoint = self.check_SoC(new_battery_setpoint, current_SoC)
        #else:
            # it is not the highest priority so see if something can be done
            #print("Demand Charge is the priority number " + str(i + 1))

        return new_SoC, new_battery_setpoint, new_grid_load
        
    def set_price_forecast(self):
        """ Set the f_DA attribute

        Args:
            forecasted_price (float x 48): cleared price in $/kWh
        """
        self.price_predict = deepcopy(self.price_data)


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
        self.price_data['Time'] = pd.to_datetime(self.price_data['Time'].values)
        self.price_data.set_index('Time')

        # self.load_data = self.load_data[
        #     (self.load_data['Time'] >= self.StartTime) & (self.load_data['Time'] < self.EndTime)]
        if len(self.price_data['Time']) == 0:
            print("load data is not in the StartTime and EndTime range")
        if len(self.price_data['Time']) < self.windowLength * 365:
            print("load data is not for the whole year")


    def set_hourly_load_forecast(self, current_time, forecast_time):
        """ Set the f_DA attribute

        Args:
            Forecasted Load (float x 48): in kW, kVar
        """
        # print("load data time", self.load_data['Time'])
        # print("current_time", current_time)
        self.load_predict = self.load_data[(self.load_data['Time'] >= current_time) & (self.load_data['Time'] < forecast_time)]['Value'].values
        self.load_up = self.load_predict + self.load_predict*self.load_dev
        self.load_down = self.load_predict - self.load_predict*self.load_dev
        self.load_predict = self.load_predict + (self.load_dev*np.random.rand(len(self.load_predict))*self.load_up)-(self.load_dev*np.random.rand(len(self.load_predict))*self.load_down)
        # because we know the forecast at the current time step
        # self.load_up[0] = self.load_predict[0]
        # self.load_down[0] = self.load_predict[0]
        self.grid_original_apparant_power = np.sqrt(self.load_predict**2 + (self.load_pf*self.load_predict)**2)
        self.grid_original_power_factor = (self.load_predict+1e-4)/(self.grid_original_apparant_power+1e-4)


    def set_load_actual(self, load_val):
        self.actual_load.append(load_val + (self.load_dev*np.random.randn(1)[0]*load_val*0.01)-(self.load_dev*np.random.randn(1)[0]*load_val*0.05))

        # temp = deepcopy(DA_SW_prices)
        # temp = np.array(temp)
        # if self.fristRun:
        #     self.fristRun = False
        #     self.retail_price_forecast = (np.roll(temp, -1)).tolist()
        # else:
        #     deltaP = np.array(self.retail_price_forecast) - temp
        #     a = 0.2
        #     k = np.flip((np.arange(1, 49, 1)))
        #     alpha = a / (k ** 0.5)
        #     temp = np.array(self.retail_price_forecast) - alpha * deltaP
        #
        #     temp = (np.roll(temp, -1)).tolist()
        #
        #     self.retail_price_forecast = deepcopy(temp)

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

        return temp


    def con_rule_ine1_demand_chg(self, m, i):
        if self.use_case_dict["demand_charge"]["control_type"] == "opti-based":
            return m.beta_D + m.eta_D[i] >= (self.load_up[i] - self.load_down[i])
        else:
            return m.beta_D + m.eta_D[i] == 0.0

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



    def DA_optimal_quantities(self):
        """ Generates Day Ahead optimized quantities for Battery

        Returns:
            Quantity (float) (1 x windowLength): Optimal quantity from optimization for all hours of the window specified by windowLength
        """

        model = pyo.ConcreteModel()
        model.p_dis = pyo.Var(self.TIME, bounds=(0, self.rated_kW))
        model.p_chg = pyo.Var(self.TIME, bounds=(0, self.rated_kW))
        model.p_batt = pyo.Var(self.TIME)
        model.q_batt = pyo.Var(self.TIME)

        model.p_total = pyo.Var(self.TIME, bounds=(0, None))
        model.q_total = pyo.Var(self.TIME)

        model.SoC = pyo.Var(self.TIME, bounds=(self.reserve_SoC, self.rated_kWh-self.reserve_SoC))

        model.p_peak = pyo.Var(bounds=(0, None))

        model.eta_D = pyo.Var(self.TIME, bounds=(0, None))
        model.beta_D = pyo.Var(bounds = (0, None))

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
                #self.grid_apparent_power[t] = np.sqrt(self.grid_react_power_prediction[t]**2 + self.grid_load_prediction[t]**2)
                #self.grid_power_factor[t] = (self.grid_load_prediction[t]+1e-6)/(self.grid_apparent_power[t]+1e-6)
                self.grid_apparent_power_prediction[t] = self.get_apparent_power(self.grid_load_prediction[t], self.grid_react_power_prediction[t])
                self.grid_power_factor_prediction[t] = self.get_power_factor(self.grid_load_prediction[t], self.grid_apparent_power_prediction[t])
            self.peak_load_prediction = pyo.value(model.p_peak)
        except:
            print('Optimization Failed')
        # return p_batt_val, p_chg_val, p_dis_val, soc_val, p_peak_val, p_total_val

        # def rt_control_demand_charge(self):


if __name__ == "__main__":
    """Testing

    Makes a single battery agent and run DA 
    """


