#   Copyright (C) 2017-2018 Battelle Memorial Institute
# file: process_pypower.py

from datetime import datetime, date, timedelta
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from collections import defaultdict


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
    # ds = [d1, d2]
    # d = {}
    # for k in d1.keys():
    #     d[k] = tuple(d[k] for d in ds)
    # return d
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
                ax.plot(x_array_flat, y_array_flat, label=str(plot_1_variables_rt[i]), linewidth=3.0)
            else:
                ax.plot(x_array_flat, y_array_flat, label=str(plot_1_variables_rt[i]), linewidth=2.0)

            y = da_data[plot_1_variables_da[i]][j]
            y_array = np.array(y)
            y_array_flat = np.reshape(y_array, -1)
            if plot_1_variables_da[i] == 'peak_load_da':
                ax.plot(x_array_flat, y_array_flat[x_array_flat-(time_lag*j)], label=str(plot_1_variables_da[i]), linestyle='--', linewidth=3.0)
            else:
                ax.plot(x_array_flat,  y_array_flat[x_array_flat-(time_lag*j)], label=str(plot_1_variables_da[i]), linestyle='--', linewidth=2.0)

    ax.set_ylabel('kW')
    ax.set_xlabel('Seconds')

    ax.set_title('DA vs RT Dispatch')

    ax.legend()
    ax.grid(True)


def plot_continous(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_files, fig_name):

    time_lag = 24 * 60 * 60


    idx = []


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



    df_da.plot(x='Time', y=plot_1_variables_da[1:], kind='line', title='Day-Ahead Dispatch', grid=True)
    plt.savefig(fig_name + '_' + str(plot_1_variables_da[1]) +'_DA_results.png')

    df_rt.plot(x='Time', y=plot_1_variables_rt[1:], kind='line', title='Real-Time Dispatch', grid=True)
    plt.savefig(fig_name + '_' + str(plot_1_variables_rt[1]) +'RT_Dispatch.png')

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

folder_name = 'results_pictures\\'
case_name = 'sensitivity'
fig_name = folder_name + case_name
# no_of_data_files = 5

# ts = ["86400", "172800", "259200", "345600", "432000", "518400"]
ts = ["86400", "172800", "259200"]
no_of_data_files = len(ts)

# ts = ["86400"]
da_data = {}
rt_data = {}
# for i in range(0, len(ts)):
#
#     da_name = folder + "\\" + str(ts[i]) + posfile_da + ".json"
#     rt_name = folder + "\\" + str(ts[i]) + posfile_rt + ".json"
#
#     dict_da = open(da_name).read()
#     if i > 0:
#         da_data = mergeDictNew(da_data, json.loads(dict_da))
#
#     else:
#         da_data = json.loads(dict_da)
#
#     dict_rt = open(rt_name).read()
#     if i > 0:
#         rt_data = mergeDictNew(rt_data, json.loads(dict_rt))
#     else:
#         rt_data = json.loads(dict_rt)
dict_da_data = []
dict_rt_data = []
for i in range(0, len(ts)):

    da_name = folder + "\\" + str(ts[i]) + posfile_da + ".json"
    rt_name = folder + "\\" + str(ts[i]) + posfile_rt + ".json"

    dict_da = open(da_name).read()
    dict_da_data.append(json.loads(dict_da))

    dict_rt = open(rt_name).read()
    dict_rt_data.append(json.loads(dict_rt))


da_data = mergeDicts(dict_da_data)
rt_data = mergeDicts(dict_rt_data)

# ===================== plots to check optimization results ===============
# fig, ax = plt.subplots()

# {'Time': [], 'battery_setpoints_rt': [], 'SoC_rt': [], 'grid_load_rt': [], 'peak_load_rt': [],
#                 'react_grid_rt': [], 'react_batt_rt': [], 'grid_pf_rt': [], 'total_load_actual_rt': []}

plot_1_variables_da = ['Time', 'battery_setpoints_da', 'grid_load_da', 'total_load_predict_da', 'peak_load_da']
plot_1_variables_rt = ['Time', 'battery_setpoints_rt', 'grid_load_rt', 'total_load_actual_rt', 'peak_load_rt']

plot_continous(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name)



#
plot_2_variables_da = ['Time', 'SoC_da']
plot_2_variables_rt = ['Time', 'SoC_rt']
plot_continous(plot_2_variables_da, plot_2_variables_rt, da_data, rt_data, no_of_data_files, fig_name)

plot_3_variables_da = ['Time', 'react_grid_da',  'react_batt_da']
plot_3_variables_rt =  ['Time', 'react_grid_rt',  'react_batt_rt']
plot_continous(plot_3_variables_da, plot_3_variables_rt, da_data, rt_data, no_of_data_files, fig_name)

plot_4_variables_da = ['Time', 'grid_pf_da']
plot_4_variables_rt =  ['Time', 'grid_pf_rt']
plot_continous(plot_4_variables_da, plot_4_variables_rt, da_data, rt_data, no_of_data_files, fig_name)


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

