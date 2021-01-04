#   Copyright (C) 2017-2018 Battelle Memorial Institute
# file: process_pypower.py

from datetime import datetime, date, timedelta
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib import rc

from collections import defaultdict
font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 18}

rc('font', **font)

import json

def mergeDict(dict1, dict2):
   ''' Merge dictionaries and keep values of common keys in list'''
   dict3 = {**dict1, **dict2}
   for key, value in dict3.items():
       if key in dict1 and key in dict2:
            # dict3[key].append([dict1[key]]) value.append(dict1[key])
            dict3[key] = [value , dict1[key]]

   return dict3

#
# d1 = {1: 2, 3: 4}
# d2 = {1: 6, 3: 7}

def mergeDicts(dict_list):

    dd = defaultdict(list)


    # for d in (d1, d2):
    for d in dict_list:
        for key, value in d.items():
            dd[key].append(value)

    return dd


def plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_files):
    time_lag = 24*60*60
    fig, ax = plt.subplots(1, 2, sharey=True)

    for j in range(no_of_files):

        x = rt_data['Time'][j]
        x_array = np.array(x)
        x_array_flat = np.reshape(x_array, -1)

        for i in range(len(plot_1_variables_da)):
            y = rt_data[plot_1_variables_rt[i]][j]
            y_array = np.array(y)
            y_array_flat = np.reshape(y_array, -1)
            ax[1].plot(x_array_flat, y_array_flat, label=str(plot_1_variables_rt[i]), linestyle='--', linewidth=2.0)

            y = da_data[plot_1_variables_da[i]][j]
            y_array = np.array(y)
            y_array_flat = np.reshape(y_array, -1)
            ax[0].plot(x_array_flat, y_array_flat[x_array_flat-(time_lag*j)], label=str(plot_1_variables_da[i]), linewidth=2.0)



    ax[0].set_ylabel('kW')
    ax[0].set_xlabel('Seconds')
    ax[1].set_xlabel('Seconds')

    ax[0].set_title('DA Dispatch')
    ax[1].set_title('Real-Time Dispatch')

    ax[0].legend()
    ax[1].legend()
    ax[0].grid(True)
    ax[1].grid(True)


def plot_single(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_files):
    time_lag = 24*60*60

    fig, ax = plt.subplots()

    for j in range(no_of_files):

        x = rt_data['Time'][j]
        x_array = np.array(x)
        x_array_flat = np.reshape(x_array, -1)

        for i in range(len(plot_1_variables_da)):
            y = rt_data[plot_1_variables_rt[i]][j]
            y_array = np.array(y)
            y_array_flat = np.reshape(y_array, -1)
            if plot_1_variables_rt[i] == 'peak_load_rt':
                ax.plot(x_array_flat, y_array_flat, label=str(plot_1_variables_rt[i]), linewidth=4.0)
            else:
                ax.plot(x_array_flat, y_array_flat, label=str(plot_1_variables_rt[i]), linewidth=3.0)

            y = da_data[plot_1_variables_da[i]][j]
            y_array = np.array(y)
            y_array_flat = np.reshape(y_array, -1)
            if plot_1_variables_da[i] == 'peak_load_da':
                ax.plot(x_array_flat, y_array_flat[x_array_flat-(time_lag*j)], label=str(plot_1_variables_da[i]), linestyle='--', linewidth=4.0)
            else:
                ax.plot(x_array_flat,  y_array_flat[x_array_flat-(time_lag*j)], label=str(plot_1_variables_da[i]), linestyle='--', linewidth=3.0)

    ax.set_ylabel('kW')
    ax.set_xlabel('Seconds')

    ax.set_title('DA vs RT Dispatch')

    ax.legend()
    ax.grid(True)


def plot_continous(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_files, fig_name):



    df_rt = pd.DataFrame(columns=plot_1_variables_rt)
    df_rt.set_index('Time')
    df_da = pd.DataFrame(columns=plot_1_variables_da)
    df_da.set_index('Time')
    idx = []
    for j in range(no_of_files):
        x = rt_data['Time'][j]
        x_array = np.array(x)
        x_array_flat = np.reshape(x_array, -1)
        idx.append(x_array_flat)
    idx_array = np.array(idx)
    idx_flat = np.reshape(idx_array, -1)
    idx_array_flat = np.array(idx_flat)
    df_da['Time'] = idx_array_flat
    df_rt['Time'] = idx_array_flat
    for j in range(no_of_files):
        x = rt_data['Time'][j]
        x_array = np.array(x)
        x_array_flat = np.reshape(x_array, -1)
        for i in range(1,len(plot_1_variables_da)):
            y = rt_data[plot_1_variables_rt[i]][j]
            y_array = np.array(y)
            y_array_flat = np.reshape(y_array, -1)
            df_rt.loc[x_array_flat, plot_1_variables_rt[i]] = y_array_flat


            y_da = da_data[plot_1_variables_da[i]][j]
            y_da_array = np.array(y_da)
            y_da_array_flat = np.reshape(y_da_array, -1)
            df_da.loc[x_array_flat, plot_1_variables_da[i]] = y_da_array_flat

    findPriceColumn_da = [match for match in plot_1_variables_da if "price_predict_da" in match]

    if len(findPriceColumn_da) > 0:
        new_var_idx = []
        for i in range(0, len(plot_1_variables_da)):
            if plot_1_variables_da[i] is not findPriceColumn_da[0]:
                new_var_idx.append(plot_1_variables_da[i])

        ax1 = df_da.plot(x='Time', y=new_var_idx[1:], kind='line', title='Day-Ahead Dispatch', grid=True)
        ax2 = df_da[findPriceColumn_da[0]].plot(secondary_y=True, color='grey', grid=True, legend='DA Price Predict')
        ax1.set_ylabel('kW')
        ax2.set_ylabel('$/kWh')
        plt.savefig(fig_name + '_' + str(plot_1_variables_da[1]) +'_DA_results_day.png')

    else:
        df_da.plot(x='Time', y=plot_1_variables_da[1:], kind='line', title='Day-Ahead Dispatch', grid=True)
        plt.savefig(fig_name + '_' + str(plot_1_variables_da[1]) +'_DA_results_day.png')

    findPriceColumn_rt = [match for match in plot_1_variables_rt if "price_actual_rt" in match]

    if len(findPriceColumn_rt) > 0:
        new_var_idx = []
        for i in range(0, len(plot_1_variables_rt)):
            if plot_1_variables_rt[i] is not findPriceColumn_rt[0]:
                new_var_idx.append(plot_1_variables_rt[i])

        ax1 = df_rt.plot(x='Time', y=new_var_idx[1:], kind='line', title='Day-Ahead Dispatch', grid=True)
        ax2 = df_rt[findPriceColumn_rt[0]].plot(secondary_y=True, color='grey', grid=True, legend='RT Price')
        ax1.set_ylabel('kW')
        ax2.set_ylabel('$/kWh')
        plt.savefig(fig_name + '_' + str(plot_1_variables_rt[1]) +'RT_Dispatch_day.png')

    else:
        df_rt.plot(x='Time', y=plot_1_variables_rt[1:], kind='line', title='Real-Time Dispatch', grid=True)
        plt.savefig(fig_name + '_' + str(plot_1_variables_rt[1]) +'RT_Dispatch_day.png')

    # plt.show()


    # ax.set_ylabel('kW')
    # ax.set_xlabel('Seconds')
    #
    # ax.set_title('DA vs RT Dispatch')
    #
    # ax.legend()
    # ax.grid(True)



def plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_files, fig_name):




    df_rt = pd.DataFrame(columns=plot_1_variables_rt)
    df_rt.set_index('Time')
    df_da = pd.DataFrame(columns=plot_1_variables_da)
    df_da.set_index('Time')
    idx = []
    for j in range(no_of_files):
        x = rt_data['Time'][j]
        x_array = np.array(x)
        x_array_flat = np.reshape(x_array, -1)
        idx.append(x_array_flat)
    idx_array = np.array(idx)
    idx_flat = np.reshape(idx_array, -1)
    idx_array_flat = np.array(idx_flat)
    df_da['Time'] = idx_array_flat
    df_rt['Time'] = idx_array_flat
    for j in range(no_of_files):
        x = rt_data['Time'][j]
        x_array = np.array(x)
        x_array_flat = np.reshape(x_array, -1)
        for i in range(1,len(plot_1_variables_da)):
            y = rt_data[plot_1_variables_rt[i]][j]
            y_array = np.array(y)
            y_array_flat = np.reshape(y_array, -1)
            df_rt.loc[x_array_flat, plot_1_variables_rt[i]] = y_array_flat


            y_da = da_data[plot_1_variables_da[i]][j]
            y_da_array = np.array(y_da)
            y_da_array_flat = np.reshape(y_da_array, -1)
            df_da.loc[x_array_flat, plot_1_variables_da[i]] = y_da_array_flat


    fig, ax = plt.subplots(figsize=(19.20,10.80))

    for i in range(0, len(plot_1_variables_da)-1):
        if plot_1_variables_da[i+1] == 'price_predict_da':
            axsec = ax.twinx()
            axsec.plot(df_da['Time'].values, df_da[plot_1_variables_da[i+1]].values, label=plot_1_variables_da[i+1], color = 'grey',  linestyle='-.', linewidth=4.0)
            axsec.plot(df_da['Time'].values, df_rt[plot_1_variables_rt[i+1]].values, label=plot_1_variables_rt[i+1], color = 'grey', linewidth=3.0)
            axsec.set_ylabel('$/kWh')
            axsec.legend(loc='lower right')
        else:
            ax.plot(df_da['Time'].values, df_da[plot_1_variables_da[i+1]].values, label=plot_1_variables_da[i+1], linestyle='-.', linewidth=4.0 )
            ax.plot(df_da['Time'].values, df_rt[plot_1_variables_rt[i+1]].values, label=plot_1_variables_rt[i+1], linewidth=3.0)

    ax.set_ylabel('kW')
    ax.legend(loc='upper right')
    # axsec.set_ylim(0.005, 0.04)
    ax.grid(True)
    # axsec.grid(True)
    plt.savefig(fig_name + '_' + str(plot_1_variables_rt[1]) +'DA_vs_RT_high_demand_chg_priority_day.png')

    # plt.show()


    # ax.set_ylabel('kW')
    # ax.set_xlabel('Seconds')
    #
    # ax.set_title('DA vs RT Dispatch')
    #
    # ax.legend()
    # ax.grid(True)



folder = "results_data"
posfile_da = "_da"
posfile_rt = "_rt"
posfile_results = "_results"
folder_name = 'results_pictures\\'
case_name = 'arbitrage'
# fig_name = folder_name + case_name
days_to_plot = 3
ts = [str(i) for i in np.arange(86400, 86400*days_to_plot, 86400)]


# ts = ["86400", "172800", "259200", "345600", "432000", "518400", "604800", "691200", "777600", "864000"]#, "950400", "1036800", "1123200"]
# ts = ["86400", "172800"]
no_of_data_files = len(ts)

fig_name = folder_name + case_name + str(no_of_data_files)


# ts = ["86400"]
da_data = {}
rt_data = {}
results_data = {}

dict_da_data = []
dict_rt_data = []
dict_results_data = []
for i in range(0, len(ts)):

    da_name = folder + "\\" + str(ts[i]) + posfile_da + ".json"
    rt_name = folder + "\\" + str(ts[i]) + posfile_rt + ".json"
    results_name = folder + "\\" + str(ts[i]) + posfile_results + ".json"

    dict_da = open(da_name).read()
    dict_da_data.append(json.loads(dict_da))

    dict_rt = open(rt_name).read()
    dict_rt_data.append(json.loads(dict_rt))

    dict_results = open(results_name).read()
    dict_results_data.append(json.loads(dict_results))

da_data = mergeDicts(dict_da_data)
rt_data = mergeDicts(dict_rt_data)
results_data = mergeDicts(dict_results_data)

metrics_idx = ['arbitrage_revenue_da', 'peak_surcharge_da', 'arbitrage_revenue_ideal_rt', 'arbitrage_revenue_actual_rt', 'peak_surcharge_rt', 'original_surcharge']
df_results = pd.DataFrame(columns=metrics_idx)
# df_results.set_index('Time')

for k in range(len(metrics_idx)):
    arr = np.array(results_data[metrics_idx[k]])
    df_results[metrics_idx[k]] = arr.reshape(-1)


# barplot1_names = ['DA Surcharge', 'RT Surcharge', 'RT Surcharge Loss']
barplot1_vals = [max(df_results[metrics_idx[5]])-max(df_results[metrics_idx[1]]), max(df_results[metrics_idx[5]])-max(df_results[metrics_idx[4]].values), max(df_results[metrics_idx[1]].values)-max(df_results[metrics_idx[4]].values)]

# barplot2_names = ['DA Arbitrage', 'RT Arbitrage', 'RT Arbitrage Loss']
barplot2_vals = [sum(df_results[metrics_idx[0]]), sum(df_results[metrics_idx[3]].values), sum(df_results[metrics_idx[3]].values)-sum(df_results[metrics_idx[0]].values)]

barWidth=0.25
br1 = np.arange(len(barplot1_vals))
br2 = [x + barWidth for x in br1]
fig = plt.subplots(figsize =(10, 6))

b1 = plt.bar(br1, barplot1_vals, color='r', width=barWidth, edgecolor= 'grey')
b2 = plt.bar(br2, barplot2_vals, color='g', width=barWidth, edgecolor= 'grey')

# plt.xlabel('Ti', fontweight='bold')
plt.ylabel('$', fontweight='bold')
plt.xticks([r + barWidth/2 for r in range(len(barplot1_vals))],
           ['DA', 'RT', 'Diff.'])
plt.legend((b1[0], b2[0]), ('Surcharge Red.', 'Arbitrage Rev.'))
plt.grid(True)
plt.savefig(fig_name + '_metrics' + 'DA_vs_RT_high_demand_chg_priority_days.png')

# ===================== plots to check optimization results ===============


plot_1_variables_da = ['Time', 'battery_setpoints_da', 'arbitrage_purchased_power_da',  'price_predict_da']
plot_1_variables_rt = ['Time', 'battery_setpoints_rt', 'arbitrage_purchased_power_actual_rt',  'price_actual_rt']

# plot_1_variables_da = ['Time', 'arbitrage_purchased_power_da', 'arbitrage_purchased_power_da']
# plot_1_variables_rt = ['Time', 'arbitrage_purchased_power_ideal_rt', 'arbitrage_purchased_power_actual_rt']


plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name)
#
# plot_1_variables_da = ['Time', 'grid_load_da', 'peak_load_da']
# plot_1_variables_rt = ['Time', 'grid_load_rt',  'peak_load_rt']

# plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name)

plot_1_variables_da = ['Time', 'total_load_predict_da', 'peak_load_da', 'grid_load_da']
plot_1_variables_rt = ['Time', 'total_load_actual_rt',  'peak_load_rt', 'grid_load_rt']
#
#
plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name)
# #
# plot_1_variables_da = ['Time', 'grid_pf_da']
# plot_1_variables_rt = ['Time', 'grid_pf_rt']
#
# plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name)
# #
# plot_1_variables_da = ['Time', 'react_grid_da', 'react_batt_da']
# plot_1_variables_rt = ['Time', 'react_grid_rt', 'react_batt_rt']
#
# plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name)
#
# plot_1_variables_da = ['Time', 'SoC_da']
# plot_1_variables_rt = ['Time', 'SoC_rt']
# plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name)

#
# #
# plot_2_variables_da = ['Time', 'SoC_da']
# plot_2_variables_rt = ['Time', 'SoC_rt']
# plot_continous(plot_2_variables_da, plot_2_variables_rt, da_data, rt_data, no_of_data_files, fig_name)
#
# plot_3_variables_da = ['Time', 'react_grid_da',  'react_batt_da']
# plot_3_variables_rt =  ['Time', 'react_grid_rt',  'react_batt_rt']
# plot_continous(plot_3_variables_da, plot_3_variables_rt, da_data, rt_data, no_of_data_files, fig_name)
#
# plot_4_variables_da = ['Time', 'grid_pf_da']
# plot_4_variables_rt = ['Time', 'grid_pf_rt']
# plot_continous(plot_4_variables_da, plot_4_variables_rt, da_data, rt_data, no_of_data_files, fig_name)
#

#
# plot_3_variables_comp = ['Time','battery_setpoints_da', 'battery_setpoints_rt']
# plot_4_variables_comp = ['Time','grid_load_da', 'grid_load_rt']


#
# plot_1_variables_da = ['battery_setpoints_da', 'grid_load_da', 'total_load_predict_da', 'peak_load_da']
# plot_1_variables_rt = ['battery_setpoints_rt', 'grid_load_rt', 'total_load_actual_rt', 'peak_load_rt']
# plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, len(ts))
#
# plot_single(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, len(ts))

# plot_continous(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, len(ts))
#
# plot_continous(plot_2_variables_da, plot_2_variables_rt, da_data, rt_data, len(ts))
#

plt.show()

