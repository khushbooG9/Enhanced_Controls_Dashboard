#   Copyright (C) 2017-2018 Battelle Memorial Institute
# file: process_pypower.py

from datetime import datetime, date, timedelta
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt


import json

def mergeDict(dict1, dict2):
   ''' Merge dictionaries and keep values of common keys in list'''
   dict3 = {**dict1, **dict2}
   for key, value in dict3.items():
       if key in dict1 and key in dict2:
               dict3[key] = [value , dict1[key]]

   return dict3


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


def plot_continous(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_files):

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
    df_rt.plot(x='Time', y=plot_1_variables_rt[1:], kind='line', title='Real-Time Dispatch', grid=True)
    # plt.show()


    # ax.set_ylabel('kW')
    # ax.set_xlabel('Seconds')
    #
    # ax.set_title('DA vs RT Dispatch')
    #
    # ax.legend()
    # ax.grid(True)


folder = "results_folder"
posfile_da = "_da"
posfile_rt = "_rt"
ts = ["86400", "172800"]
da_data = {}
rt_data = {}
for i in range(0, len(ts)):

    da_name = folder + "\\" + str(ts[i]) + posfile_da + ".json"
    rt_name = folder + "\\" + str(ts[i]) + posfile_rt + ".json"

    dict_da = open(da_name).read()
    if i > 0:
        da_data = mergeDict(json.loads(dict_da), da_data)

    else:
        da_data = json.loads(dict_da)

    dict_rt = open(rt_name).read()
    if i > 0:
        rt_data = mergeDict(json.loads(dict_rt), rt_data)
    else:
        rt_data = json.loads(dict_rt)


# ===================== plots to check optimization results ===============
# fig, ax = plt.subplots()

# plot_1_variables_da = ['Time', 'battery_setpoints_da', 'grid_load_da', 'total_load_predict_da', 'peak_load_da']
# plot_1_variables_rt = ['Time', 'battery_setpoints_rt', 'grid_load_rt', 'total_load_actual_rt', 'peak_load_rt']
# plot_continous(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, len(ts))

# plot_continous(plot_2_variables_da, plot_2_variables_rt, da_data, rt_data, len(ts))


#
#
# plot_2_variables_da = ['Time', 'SoC_da']
# plot_2_variables_rt = ['Time', 'SoC_rt']
#
# plot_3_variables_comp = ['Time','battery_setpoints_da', 'battery_setpoints_rt']
# plot_4_variables_comp = ['Time','grid_load_da', 'grid_load_rt']


#
plot_1_variables_da = ['battery_setpoints_da', 'grid_load_da', 'total_load_predict_da', 'peak_load_da']
plot_1_variables_rt = ['battery_setpoints_rt', 'grid_load_rt', 'total_load_actual_rt', 'peak_load_rt']
plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, len(ts))

plot_single(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, len(ts))

# plot_continous(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, len(ts))
#
# plot_continous(plot_2_variables_da, plot_2_variables_rt, da_data, rt_data, len(ts))
#

plt.show()

# fig, ax = plt.subplots(2,1, sharex=True)
# ax[0].plot(battery_obj.grid_react_power_prediction, label='Total Reactive Power Grid ')
# ax[0].plot(battery_obj.battery_react_power_prediction, label='Reactive Power Battery')
# ax[0].plot(battery_obj.load_up*battery_obj.load_pf, label='Predicted Reactive Power Load')
#
# ax[0].set_ylabel('kVar')
# ax[0].set_title('Reactive Power')
# ax[0].legend()
# ax[0].set_title('Grid Side Results')
# ax[0].grid(True)
#
# ax[1].plot(battery_obj.grid_power_factor, label='New Power Factor')
# ax[1].plot(battery_obj.grid_original_power_factor, label='Old Power Factor', dashes=[4,4])
# ax[1].set_xlabel('Hours')
# ax[1].set_ylabel('cosphi')
# ax[1].legend()
# ax[1].grid(True)
# ax[1].set_ylim([0, 1.02])
#
# plt.show()
