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
        'size'   : 28}

rc('font', **font)

# import matplotlib
# matplotlib.use("pgf")
# matplotlib.rcParams.update({
#     "pgf.texsystem": "pdflatex",
#     'font.family': 'serif',
#     'text.usetex': True,
#     'pgf.rcfonts': False,
# })

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



def plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_files, fig_name, legend_names_da, legend_names_rt, days_to_plot):

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

    check_plots = 1
    customdate = datetime(2019, 1, 1, 12, 0)
    x = [customdate + timedelta(seconds=i) for i in range(len(df_da['Time'].values))]
    skip_next = False
    fig, ax = plt.subplots(figsize=(19.20,10.80))

    for i in range(0, len(plot_1_variables_da)-1):

        if plot_1_variables_da[i+1] == 'price_predict_da' or plot_1_variables_da[i+1] == 'reg_price_predict_up' or  plot_1_variables_da[i+1] == 'reg_price_predict_down':
            axsec = ax.twinx()
            # axsec.plot(df_da['Time'].values, df_da[plot_1_variables_da[i+1]].values, label=legend_names_da[i+1], color = 'grey',  linestyle='-.', linewidth=4.0)
            # axsec.plot(df_da['Time'].values, df_rt[plot_1_variables_rt[i+1]].values, label=legend_names_rt[i+1], color = 'grey', linewidth=3.0)
            axsec.plot(x, df_da[plot_1_variables_da[i + 1]].values, label=legend_names_da[i + 1],
                       color='grey', linestyle='-.', linewidth=5.0)
            axsec.plot(x, df_rt[plot_1_variables_rt[i + 1]].values, label=legend_names_rt[i + 1],
                       color='grey', linewidth=4.0)
            axsec.set_ylabel('$/kWh')
            axsec.legend(loc='lower right')
        else:
            if plot_1_variables_da[i + 1] == 'reg_up_cap_da':

                #x = idx_array_flat
                y1 = (np.array(df_da['battery_setpoints_da'].values) + np.array(df_da[plot_1_variables_da[i + 1]].values)*5/60).tolist()
                y2 = (np.array(df_da['battery_setpoints_da'].values) + np.array(-df_da[plot_1_variables_da[i + 2]].values)*5/60).tolist()
                # plt.fill_between(x, y1, y2, label='reg_capacity_da', facecolor="tab:brown", edgecolor='blue', alpha=0.5)
                plt.fill_between(x, y1, y2, label=legend_names_da[i + 1], facecolor="tab:brown", edgecolor='blue', alpha=0.5)

                y1 = (np.array(df_rt['battery_setpoints_rt'].values) + np.array(df_rt[plot_1_variables_rt[i + 1]].values)*5/60).tolist()
                y2 = (np.array(df_rt['battery_setpoints_rt'].values) + np.array(-df_rt[plot_1_variables_rt[i + 2]].values)*5/60).tolist()
                # plt.fill_between(x, y1, y2, label='reg_capacity_rt', facecolor="tab:brown", edgecolor='black', alpha=0.2)
                plt.fill_between(x, y1, y2, label=legend_names_rt[i + 1], facecolor="tab:brown", edgecolor='black', alpha=0.2)

                skip_next = True


            elif skip_next is False:
                if plot_1_variables_da[i + 1] == 'peak_load_da':
                    # ax.plot(df_da['Time'].values, np.max(df_da[plot_1_variables_da[i + 1]].values)*np.ones(len(df_da['Time'])),
                    #        label=legend_names_da[i+1], linestyle='-.', linewidth=4.0)
                    # ax.plot(df_da['Time'].values,
                    #         np.max(df_rt[plot_1_variables_rt[i + 1]].values) * np.ones(len(df_rt['Time'])),
                    #         label=legend_names_rt[i+1], linestyle='-.', linewidth=3.0)
                    ax.plot(x,
                            np.max(df_da[plot_1_variables_da[i + 1]].values) * np.ones(len(df_da['Time'])),
                            label=legend_names_da[i + 1], linestyle='-.', linewidth=5.0)
                    ax.plot(x,
                            np.max(df_rt[plot_1_variables_rt[i + 1]].values) * np.ones(len(df_rt['Time'])),
                            label=legend_names_rt[i + 1], linestyle='-.', linewidth=4.0)
                else:
                    # ax.plot(df_da['Time'].values, df_da[plot_1_variables_da[i+1]].values, label=legend_names_da[i+1], linestyle='-.', linewidth=4.0 )
                    # ax.plot(df_da['Time'].values, df_rt[plot_1_variables_rt[i+1]].values, label=legend_names_rt[i+1], linewidth=3.0)
                    ax.plot(x, df_da[plot_1_variables_da[i+1]].values, label=legend_names_da[i+1], linestyle='-.', linewidth=5.0 )
                    ax.plot(x, df_rt[plot_1_variables_rt[i+1]].values, label=legend_names_rt[i+1], linewidth=4.0)
            else:
                skip_next = False
    if plot_1_variables_da[len(plot_1_variables_da)-1] == 'SoC_da':
        ax.set_ylabel('kWh')
    elif plot_1_variables_da[len(plot_1_variables_da)-1] == 'grid_pf_da':
        ax.set_ylabel('cos(phi)')
        ax.set_ylim(0.95, 1.01)
    elif plot_1_variables_da[len(plot_1_variables_da)-1] == 'react_batt_da':
        ax.set_ylabel('kVar')
    else:
        ax.set_ylabel('kW')

    ax.legend(loc='upper right')
    # axsec.set_ylim(0.005, 0.04)
    ax.grid(True)
    # axsec.grid(True)
    plt.gcf().autofmt_xdate()
    plt.savefig(fig_name + '_' + str(days_to_plot) + str(plot_1_variables_rt[1]) +'DA_vs_RT_high_demand_chg_priority_day.png', dpi=300)
    # plt.savefig(fig_name + '_' + str(plot_1_variables_rt[1]) + 'DA_vs_RT.pgf')

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
case_name = 'paper_figs'
# fig_name = folder_name + case_name
days_to_plot = 31
ts = [str(i) for i in np.arange(86400, 86400*days_to_plot, 86400)]
robustness = 'N_2'
res_per_MW = ''

no_of_data_files = len(ts)

fig_name = folder_name + case_name + str(no_of_data_files) + '_' + robustness + '_' + res_per_MW


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

    print('Reading file: '+ da_name)
    dict_da = open(da_name).read()
    dict_da_data.append(json.loads(dict_da))

    print('Reading file: '+ rt_name)
    dict_rt = open(rt_name).read()
    dict_rt_data.append(json.loads(dict_rt))

    print('Reading file: '+ results_name)
    dict_results = open(results_name).read()
    dict_results_data.append(json.loads(dict_results))

da_data = mergeDicts(dict_da_data)
rt_data = mergeDicts(dict_rt_data)
results_data = mergeDicts(dict_results_data)

metrics_idx = ['arbitrage_revenue_da',
               'peak_surcharge_da',
               'arbitrage_revenue_ideal_rt',
               'arbitrage_revenue_actual_rt',
               'peak_surcharge_rt',
               'original_surcharge',
               'reg_up_rev_da',
               'reg_down_rev_da',
               'reg_up_rev_rt',
               'reg_down_rev_rt']
df_results = pd.DataFrame(columns=metrics_idx)
# df_results.set_index('Time')

for k in range(len(metrics_idx)):
    arr = np.array(results_data[metrics_idx[k]])
    df_results[metrics_idx[k]] = arr.reshape(-1)


# arbitrage_da = sum(df_results[metrics_idx[0]])
# arbitrage_rt = sum(df_results[metrics_idx[3]].values)
# arbitrage_diff = sum(df_results[metrics_idx[3]].values)-sum(df_results[metrics_idx[0]].values)


arbitrage_da = sum(df_results[metrics_idx[0]])
arbitrage_rt = sum(df_results[metrics_idx[3]].values)
arbitrage_diff = sum(df_results[metrics_idx[3]].values)-sum(df_results[metrics_idx[0]].values)

res_da = sum(df_results[metrics_idx[6]])+sum(df_results[metrics_idx[7]])
res_rt = sum(df_results[metrics_idx[8]].values)+sum(df_results[metrics_idx[9]].values)
res_diff = sum(df_results[metrics_idx[8]].values)+sum(df_results[metrics_idx[9]].values)-sum(df_results[metrics_idx[6]].values)-sum(df_results[metrics_idx[7]].values)

# I saw literature on peak demand charge range from 1.5 to 6 $/kW, so just picking a smaller value now as compared to 6 kW based on which the simulation was run
surcharge_da = max(df_results[metrics_idx[1]])*2.5/6
surcharge_rt = max(df_results[metrics_idx[4]])*2.5/6
surcharge_diff = max(df_results[metrics_idx[1]].values)*2.5/6-max(df_results[metrics_idx[4]].values)*2.5/6

total_da = arbitrage_da + res_da - surcharge_da
total_rt = arbitrage_rt + res_rt - surcharge_rt
print('arbitrage_da_rev'+str(arbitrage_da) + ', arbitrage_rt_rev' + str(arbitrage_rt) + ', arbitrage_diff' + str(arbitrage_diff))
print('res_da_rev'+str(res_da) + ', arbitrage_rt_rev' + str(res_rt) + ', res_diff' + str(res_diff))
print('surcharge_da'+str(surcharge_da) + ', surcharge_rt' + str(surcharge_rt) + ', surcharge_diff' + str(surcharge_rt))

print('total_da_rev = ' + str(total_da) + ', total_rt_rev = ' + str(total_rt) + ' rev_diff' + str(total_rt-total_da))

barplot2_vals = [arbitrage_da, arbitrage_rt, arbitrage_diff]

barplot1_vals = [surcharge_da, surcharge_rt, surcharge_diff]

barplot3_vals = [res_da, res_rt, res_diff]

barWidth=0.25
br1 = np.arange(len(barplot1_vals))
br2 = [x - barWidth for x in br1]
br3 = [x + barWidth for x in br1]

labels = ['DA', 'RT', 'Diff.']
x = np.arange(len(labels))

fig, ax = plt.subplots(figsize =(12, 8), nrows=1, ncols=3)

ax[0].bar(x, barplot1_vals, color='r', width=barWidth, edgecolor= 'grey', label='Demand Charge')
ax[1].bar(x, barplot2_vals, color='g', width=barWidth, edgecolor= 'grey', label='Energy Arbitrage')
ax[2].bar(x, barplot3_vals, color='b', width=barWidth, edgecolor= 'grey', label='Energy Res/Reg')
ax[0].set_ylabel('$', fontweight='bold')
ax[0].set_xticks(x)
ax[0].set_xticklabels(labels)
ax[0].legend(loc='best')
ax[1].set_xticks(x)
ax[1].set_xticklabels(labels)
ax[1].legend(loc='best')
ax[2].set_xticks(x)
ax[2].set_xticklabels(labels)
ax[2].legend(loc='best')
ax[0].grid(True)
ax[1].grid(True)
ax[2].grid(True)
plt.savefig(fig_name + '_metrics' + 'DA_vs_RT_high_sep_multiservices.png')
# plt.savefig(fig_name + '_metrics' + 'DA_vs_RT_high_sep_multiservices.pgf')
# plt.show()

# ===================== plots to check optimization results ===============

plot_1_variables_da = ['Time', 'battery_setpoints_da', 'reg_up_cap_da',  'reg_down_cap_da', 'arbitrage_purchased_power_da']#, 'reg_price_predict_up']#, 'reg_price_predict_down']
plot_1_variables_rt = ['Time', 'battery_setpoints_rt', 'reg_up_cap_rt',  'reg_down_cap_rt', 'arbitrage_purchased_power_actual_rt']#, 'reg_price_up_rt']#, 'reg_price_down_rt']
legend_names_da = ['-', 'ESS Set-Point DA', 'ESS Res DA', 'ESS Res DA', 'ESS Arb DA']
legend_names_rt = ['-', 'ESS Set-Point RT', 'ESS Res RT', 'ESS Res RT', 'ESS Arb RT']

plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name, legend_names_da, legend_names_rt, days_to_plot)

# plot_1_variables_da = ['Time', 'battery_setpoints_da']#, 'reg_price_predict_up']#, 'reg_price_predict_down']
# plot_1_variables_rt = ['Time', 'battery_setpoints_rt']#, 'reg_price_up_rt']#, 'reg_price_down_rt']
# legend_names_da = ['-', 'ESS Set-Point DA', 'ESS Res DA']
# legend_names_rt = ['-', 'ESS Set-Point RT', 'ESS Res RT']

# plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name, legend_names_da, legend_names_rt,days_to_plot)



plot_1_variables_da = ['Time', 'total_load_predict_da', 'peak_load_da', 'grid_load_da']
plot_1_variables_rt = ['Time', 'total_load_actual_rt',  'peak_load_rt', 'grid_load_rt']
legend_names_da = ['-', 'Total Load DA', 'Peak Load DA', 'Grid Load DA']
legend_names_rt = ['-', 'Total Load RT', 'Peak Load RT', 'Grid Load RT']


plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name, legend_names_da, legend_names_rt, days_to_plot)
# # #
plot_1_variables_da = ['Time', 'grid_pf_da']
plot_1_variables_rt = ['Time', 'grid_pf_rt']
legend_names_da = ['-', 'Grid PF DA']
legend_names_rt = ['-', 'Grid PF RT']
plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name, legend_names_da, legend_names_rt, days_to_plot)
# #
plot_1_variables_da = ['Time', 'react_grid_da', 'react_batt_da']
plot_1_variables_rt = ['Time', 'react_grid_rt', 'react_batt_rt']
legend_names_da = ['-', 'Grid React DA', 'ESS React DA']
legend_names_rt = ['-', 'Grid React RT', 'ESS React RT']
plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name, legend_names_da, legend_names_rt, days_to_plot)
# #
plot_1_variables_da = ['Time', 'SoC_da']
plot_1_variables_rt = ['Time', 'SoC_rt']
legend_names_da = ['-', 'ESS SoC DA']
legend_names_rt = ['-', 'ESS SoC RT']
plot_side_by_side(plot_1_variables_da, plot_1_variables_rt, da_data, rt_data, no_of_data_files, fig_name, legend_names_da, legend_names_rt, days_to_plot)


plt.show()

