# Copyright (C) 2017-2019 Battelle Memorial Institute
# file: battery_dsot_v1.py # TODO: update
"""Class that controls the Battery DER

Implements the optimum schedule of charging and discharging DA; generate the bids
for DA and RT; monitor and supervisory control of GridLAB-D environment element.

The function call order for this agent is:
    initialize

    set_price_forecast(forecasted_price)

    Repeats at every hour:
        formulate_bid_da(){return BID}

        set_price_forecast(forecasted_price)

        Repeats at every 5 min:
            set_battery_SOC(fncs_str){updates C_init}

            formulate_bid_rt(){return BID}

            inform_bid(price){update RTprice}

            bid_accepted(){update inv_P_setpoint and GridLAB-D P_out if needed}


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

class BatteryClass:
    """This agent manages the battery/inverter

    Args:
        TODO: update inputs for this agent

    Attributes: #TODO: update attributes for this agent


    """

    def __init__(self, battery_dict):  # TODO: update inputs for class
        """Initializes the class
        """
        # TODO: update attributes of class
        # initialize from Args:

        with open(battery_dict, 'r', encoding='utf-8') as lp:
            battery_dict = json.load(lp)

        self.name = battery_dict["batteryName"]

        self.capacity = battery_dict["capacity"]
        self.rating = battery_dict["rating"]
        self.charge = battery_dict["charge"]
        self.efficiency = battery_dict["efficiency"]
        self.StartTime = battery_dict["StartTime"]
        self.EndTime = battery_dict["EndTime"]
        self.SimulationDays = battery_dict["SimulationDays"]
        self.FacilityLoadDataPath = battery_dict["FacilityLoadDataPath"]
        self.PriceDataPath = battery_dict["PriceDataPath"]
        self.rated_inverter_kVA = battery_dict["rated_inverter_kVA"]
        self.rated_kW = battery_dict["rated_kW"]
        self.inv_eta = battery_dict["inv_eta"]
        self.bat_eta = battery_dict["bat_eta"]
        self.rated_kWh = battery_dict["bat_capacity_kWh"]
        self.windowLength = int(24)
        self.price_dev = battery_dict["price_dev"]
        self.load_dev = battery_dict["load_dev"]
        self.load_data_resolution = battery_dict["load_data_resolution"]
        self.peak_price = battery_dict["peak_price"]
        self.pf_limit = battery_dict["pf_limit"]
        self.load_pf = battery_dict["load_pf"]
        self.pf_penalty = battery_dict["pf_penalty"]

        self.TIME = range(0, self.windowLength)
        self.demand_charge_budget = int(battery_dict["demand_charge_budget"]*self.windowLength)

        self.SoC_init = battery_dict["SoC_init"]*battery_dict["bat_capacity_kWh"]

        self.lin_segments = int(battery_dict["linearization_segments"])
        self.SEGMENTS = range(1, self.lin_segments+1)
        self.cos_terms = np.cos((np.array(self.SEGMENTS) * np.pi * (1 / self.lin_segments)))
        self.sin_terms = np.sin((np.array(self.SEGMENTS) * np.pi * (1 / self.lin_segments)))


        self.load_data = None
        self.load_predict = None
        self.load_up = None
        self.load_down = None
        self.price_data = None



        #self.p_chg_value = [[]] * self.windowLength
        #self.p_dis_value = [[]] * self.windowLength
        self.battery_setpoints = [[]] * self.windowLength
        self.SoC_prediction = [[]] * self.windowLength
        self.peak_load_prediction = None
        self.grid_load_prediction = [[]] * self.windowLength

        self.grid_react_power_prediction = [[]] * self.windowLength
        self.battery_react_power_prediction = [[]] * self.windowLength

        self.grid_apparent_power = [[]] * self.windowLength
        self.apparent_power_battery = [[]] * self.windowLength

        self.grid_power_factor = [[]] * self.windowLength

        self.grid_original_apparant_power = [[]] * self.windowLength
        self.grid_original_power_factor =  [[]] * self.windowLength



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


    def set_load_forecast(self):
        """ Set the f_DA attribute

        Args:
            forecasted_price (float x 48): cleared price in $/kWh
        """
        self.load_predict = self.load_data[(self.load_data['Time'] >= self.StartTime) & (self.load_data['Time'] < self.EndTime)]['Value'].values
        self.load_up = self.load_predict + self.load_predict*self.load_dev
        self.load_down = self.load_predict - self.load_predict*self.load_dev
        self.load_predict = self.load_predict + (self.load_dev*np.random.rand(len(self.load_predict))*self.load_up)-(self.load_dev*np.random.rand(len(self.load_predict))*self.load_down)

        self.grid_original_apparant_power = np.sqrt(self.load_predict**2 + (self.load_pf*self.load_predict)**2)
        self.grid_original_power_factor = (self.load_predict+1e-4)/(self.grid_original_apparant_power+1e-4)
    # def DA_cleared_price(self, price):
    #     """ Set the DA_cleared_price attribute
    #
    #     Args:
    #         price (float): cleared price in $/kWh
    #     """
    #     # TODO: THis is not used, do we need it?
    #     self.prev_clr_Quantity = list()
    #     self.prev_clr_Price = list()
    #     self.prev_clr_Price = deepcopy(price)
    #     self.BindingObjFunc = bool(True)
    #     for i in range(len(self.prev_clr_Price)):
    #         self.prev_clr_Quantity.append(self.from_P_to_Q_battery(self.bid_da[i], self.prev_clr_Price[i]))
    #     self.prev_clr_Price.pop(0)
    #     self.prev_clr_Quantity.pop(0)
    #     self.prev_clr_Price.append(0.0)
    #     self.prev_clr_Quantity.append(0.0)

    # def formulate_bid_da(self):
    #     """ Formulate 4 points of P and Q bids for the DA market
    #
    #     Function calls "DA_optimal_quantities" to obtain the optimal quantities
    #     for the DA market. With the quantities, the 4 point bids are formulated.
    #
    #     Before returning the BID the function resets "RT_state_maintaing_flag"
    #     wich if RT_state_maintaing is TRUE the battery will be forced to keep its
    #     state (i.e., charging or discharging).
    #
    #     Returns:
    #         BID (float) (((1,2)X4) X windowLength): store last DA market bids
    #     """
    #     #        Quantity = self.DA_optimal_quantities()
    #     Quantity = deepcopy(self.optimized_Quantity)
    #
    #     P = self.P
    #     Q = self.Q
    #     TIME = range(0, self.windowLength)
    #     CurveSlope = [0] * len(TIME)
    #     yIntercept = [-1] * len(TIME)
    #     BID = [[[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]] for i in TIME]
    #     deltaf_DA = max(self.f_DA) - min(self.f_DA)
    #
    #     for t in TIME:
    #         CurveSlope[t] = ((max(self.f_DA) - min(self.f_DA)) / (-self.Rd - self.Rc)) * (
    #                     1 + self.ProfitMargin_slope / 100)  # Remains same in all hours of the window
    #         yIntercept[t] = self.f_DA[t] - CurveSlope[t] * Quantity[t]  # Is different for each hour of the window
    #
    #         BID[t][0][Q] = -self.Rd
    #         BID[t][1][Q] = Quantity[t]
    #         BID[t][2][Q] = Quantity[t]
    #         BID[t][3][Q] = self.Rc
    #
    #         BID[t][0][P] = -self.Rd * CurveSlope[t] + yIntercept[t] + (self.ProfitMargin_intercept / 100) * deltaf_DA
    #         BID[t][1][P] = Quantity[t] * CurveSlope[t] + yIntercept[t] + (self.ProfitMargin_intercept / 100) * deltaf_DA
    #         BID[t][2][P] = Quantity[t] * CurveSlope[t] + yIntercept[t] - (self.ProfitMargin_intercept / 100) * deltaf_DA
    #         BID[t][3][P] = self.Rc * CurveSlope[t] + yIntercept[t] - (self.ProfitMargin_intercept / 100) * deltaf_DA
    #
    #     self.bid_da = deepcopy(BID)
    #
    #     self.RT_state_maintaing_flag = 0
    #
    #     return self.bid_da

    def obj_rule(self, m):
        # return sum(self.f_DA[i] * (m.E_DA_out[i] - m.E_DA_in[i]) - self.batteryLifeDegFactor * (
        #             m.E_DA_out[i] + m.E_DA_in[i]) - 0.001 * (m.E_DA_out[i] + m.E_DA_in[i]) ** 2 for i in
        #            self.TIME)
        return sum(m.eta_D[i] for i in self.TIME) \
               + self.peak_price*m.p_peak \
               + self.demand_charge_budget*m.beta_D + \
               sum(m.theta[i] for i in self.TIME)


    def con_rule_ine1(self, m, i):
        return m.beta_D + m.eta_D[i] >= (self.load_up[i] - self.load_down[i])

    def con_rule_ine2(self, m, i):
        return m.p_total[i] + m.eta_D[i] <= m.p_peak

    def con_rule_ine3(self, m, i, k):
            return m.p_batt[i]*self.cos_terms[k-1]+ m.q_batt[i]*self.sin_terms[k-1]<= self.rated_inverter_kVA


    def con_rule_ine4(self, m, i, k):
            return m.p_batt[i]*self.cos_terms[k-1]+ m.q_batt[i]*self.sin_terms[k-1] >= -self.rated_inverter_kVA

    def con_rule_ine5(self, m, i, k):
            return self.pf_limit*(m.p_total[i]*self.cos_terms[k-1] + m.q_total[i]*self.sin_terms[k-1])*self.pf_penalty\
                   <= m.theta[i]-m.p_total[i]*self.pf_penalty

    def con_rule_ine6(self, m, i, k):

        return self.pf_limit*(m.p_total[i]*self.cos_terms[k-1]+ m.q_total[i]*self.sin_terms[k-1])*self.pf_penalty\
               >= m.p_total[i]*self.pf_penalty - m.theta[i]



    def con_rule_eq4(self, m, i):
        return m.q_total[i] == self.load_pf*m.p_total[i] + m.q_batt[i]

    def con_rule_eq1(self, m, i):
        return m.p_batt[i] == -self.bat_eta*m.p_chg[i] + (1/self.bat_eta)*(m.p_dis[i] + m.eta_D[i])

    def con_rule_eq2(self, m, i):
        return m.p_total[i] == -m.p_batt[i] + self.load_up[i]

    def con_rule_eq3(self, m, i):
        if i == 0:
            return m.SoC[i] == self.SoC_init - m.p_batt[i]
        else:
            return m.SoC[i] == m.SoC[i-1] - m.p_batt[i]





    def DA_optimal_quantities(self):
        """ Generates Day Ahead optimized quantities for Battery

        Returns:
            Quantity (float) (1 x windowLength): Optimal quantity from optimization for all hours of the window specified by windowLength
        """
        # if self.Cinit > self.Cmax:
        #     self.Cinit = self.Cmax
        # if self.Cinit < self.Cmin:
        #     self.Cinit = self.Cmin


        model = pyo.ConcreteModel()
        model.p_dis = pyo.Var(self.TIME, bounds=(0, self.rated_kW))
        model.p_chg = pyo.Var(self.TIME, bounds=(0, self.rated_kW))
        model.eta_D = pyo.Var(self.TIME, bounds=(0, None))
        model.beta_D = pyo.Var(bounds = (0, None))

        model.SoC = pyo.Var(self.TIME, bounds=(0, self.rated_kWh))
        model.p_peak = pyo.Var(bounds=(0, None))
        model.p_batt = pyo.Var(self.TIME)
        model.q_batt = pyo.Var(self.TIME)

        model.p_total = pyo.Var(self.TIME, bounds=(0, None))
        # model.p_total = pyo.Var(self.TIME)
        model.q_total = pyo.Var(self.TIME)
        model.theta = pyo.Var(self.TIME, bounds = (0, None))



        model.con1 = pyo.Constraint(self.TIME, rule=self.con_rule_ine1)
        model.con2 = pyo.Constraint(self.TIME, rule=self.con_rule_ine2)
        model.con3 = pyo.Constraint(self.TIME, self.SEGMENTS, rule=self.con_rule_ine3)
        model.con4 = pyo.Constraint(self.TIME, self.SEGMENTS, rule=self.con_rule_ine4)
        model.con5 = pyo.Constraint(self.TIME, self.SEGMENTS, rule=self.con_rule_ine5)
        model.con6 = pyo.Constraint(self.TIME, self.SEGMENTS, rule=self.con_rule_ine6)

        model.con7 = pyo.Constraint(self.TIME, rule=self.con_rule_eq1)
        model.con8 = pyo.Constraint(self.TIME, rule=self.con_rule_eq2)
        model.con9 = pyo.Constraint(self.TIME, rule=self.con_rule_eq3)
        model.con10 = pyo.Constraint(self.TIME, rule=self.con_rule_eq4)


        # model.pbus_slack = pyo.Param(model.Buses, model.Scenarios, initialize=0)
        # put the parameter as mutable so it does know you want to change it later
        # model.con.deactivate() to deactivate the constraints
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
            self.battery_setpoints = [[]] * self.windowLength
            self.SoC_prediction = [[]] * self.windowLength
            self.grid_load_prediction = [[]] * self.windowLength
            # TOL = 0.00001  # Tolerance for checking bid
            for t in self.TIME:
                # if pyo.value(model.p_chg[t]) > TOL:
                #     p_chg_val[t] = pyo.value(model.p_chg[t])  # For logging
                # if pyo.value(model.E_DA_out[t]) > TOL:
                #     p_dis_val[t] = pyo.value(model.p_dis[t])
                self.SoC_prediction[t] = pyo.value(model.SoC[t])
                self.battery_setpoints[t] = pyo.value(model.p_batt[t])
                self.grid_load_prediction[t] = pyo.value(model.p_total[t])
                self.grid_react_power_prediction[t] = pyo.value(model.q_total[t])
                self.battery_react_power_prediction[t] = pyo.value(model.q_batt[t])
                self.grid_apparent_power[t] = np.sqrt(self.grid_react_power_prediction[t]**2 + self.grid_load_prediction[t]**2)
                self.grid_power_factor[t] = (self.grid_load_prediction[t]+1e-6)/(self.grid_apparent_power[t]+1e-6)
            self.peak_load_prediction = pyo.value(model.p_peak)
        except:
            print('Optimization Failed')
        # return p_batt_val, p_chg_val, p_dis_val, soc_val, p_peak_val, p_total_val



if __name__ == "__main__":
    """Testing

    Makes a single battery agent and run DA 
    """
    battery_obj = BatteryClass('dict.json')  # make object
    battery_obj.get_data()
    print(battery_obj.load_data['Value'].values)
    battery_obj.set_load_forecast()
    # print(battery_obj.load_predict)
    # print(battery_obj.load_up)
    # print(battery_obj.load_down)
    battery_obj.DA_optimal_quantities()
    print(battery_obj.battery_setpoints)
    print(battery_obj.SoC_prediction)
    print(battery_obj.peak_load_prediction)
    print(battery_obj.grid_load_prediction)
    print(battery_obj.grid_react_power_prediction)
    print(battery_obj.battery_react_power_prediction)
    # ===================== plots to check optimization results ===============
    fig, ax = plt.subplots()
    ax.plot(battery_obj.battery_setpoints, label='Battery Power (Charge/Discharge)')
    ax.plot([battery_obj.peak_load_prediction]*battery_obj.windowLength, label='Peak load')
    ax.plot(battery_obj.grid_load_prediction, label='Grid Load')
    # ax.plot(battery_obj.load_down, label='Load Lower Bound')
    # ax.plot(battery_obj.load_up, label='Load Upper Bound')
    ax.plot(battery_obj.load_predict, label='Load Prediction')

    ax.set_ylabel('kW')
    ax.set_xlabel('Hours')
    ax.set_title('Grid Side Results')
    ax.legend()
    ax.grid(True)
    plt.show()

    fig, ax = plt.subplots(2,1, sharex=True)
    ax[0].plot(battery_obj.grid_react_power_prediction, label='Total Reactive Power Grid ')
    ax[0].plot(battery_obj.battery_react_power_prediction, label='Reactive Power Battery')
    ax[0].plot(battery_obj.load_up*battery_obj.load_pf, label='Predicted Reactive Power Load')

    ax[0].set_ylabel('kVar')
    ax[0].set_title('Reactive Power')
    ax[0].legend()
    ax[0].set_title('Grid Side Results')
    ax[0].grid(True)

    ax[1].plot(battery_obj.grid_power_factor, label='New Power Factor')
    ax[1].plot(battery_obj.grid_original_power_factor, label='Old Power Factor', dashes=[4,4])
    ax[1].set_xlabel('Hours')
    ax[1].set_ylabel('cosphi')
    ax[1].legend()
    ax[1].grid(True)
    ax[1].set_ylim([0, 1.02])

    plt.show()

    # ===================== plots to check inputs =============================
    # fig, ax = plt.subplots()
    # ax.plot(battery_obj.load_up,label='load up')
    # ax.plot(battery_obj.load_down,label='load down')
    # ax.plot(battery_obj.load_predict,label='load predict')
    # ax.set_ylabel('kW')
    # ax.set_xlabel('Hours')
    # ax.set_title('Load Prediction')
    # ax.legend()
    # ax.grid(True)
    # plt.show()
    # B_obj1.set_price_forecast(price_DA.tolist())
    # quantity = B_obj1.DA_optimal_quantities()
    # print("--- %s seconds ---" % (time.time() - start_time))
    # print(quantity)
#    B = B_obj1.RT_fix_four_points_range(BID,0.2920860000000012,5.0)
#    A = B_obj1.RT_fix_four_points_range(B,0.2920860000000012,0.2920860000000012)
#    B_obj2 = BatteryDSOT(agent,glm,'test')# make object
#
#    for i in range(5):
#        B_obj1.set_price_forecast(price_DA)
#        B_obj2.set_price_forecast(price_DA)
#
#        BIDS = B_obj1.formulate_bid_da()
#        B_obj2.formulate_bid_da()
#
#        BIDS8 = B_obj1.bid_da
#
#        Quantity = B_obj1.optimized_Quantity

#    rtbid = B_obj1.formulate_bid_rt()
#    price_forecast = B_obj.f_DA
#    BIDS_of_agent = B_obj.bid_da
#    #B_obj.Cinit = B_obj.batteryCapacity * 0.5#B_obj.set_battery_SOC()
#    BID = [[-5.0,6.0],[0.0,5.0],[0.0,4.0],[5.0,3.0]]
#    fixed = B_obj.RT_fix_four_points_range(BID,0.0,10.0)
#    print(fixed)
#    fixed = B_obj.RT_fix_four_points_range(BID,-float('inf'),0.0)
#    print(fixed)
#    fixed = B_obj.RT_fix_four_points_range(BID,0.0,float('inf'))
#    print(fixed)
#    fixed = B_obj.RT_fix_four_points_range(BID,0.5,0.5)
#    print(fixed)
#    getQ = B_obj.from_P_to_Q_battery(BID,10)
#    print(getQ)
#    getQ = B_obj.from_P_to_Q_battery(fixed,10)
#    print(getQ)


