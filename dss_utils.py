import opendssdirect as dss
import os
from scipy.sparse import csc_matrix, linalg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from matplotlib.collections import LineCollection
# from matplotlib.colors import ColorConverter
# import matplotlib.text as text
# colorConverter = ColorConverter()
import matplotlib as mpl

import re
import networkx as nx

class dss_utils:
    """
    Class to collect useful opendss utilities using opendssdirect package
    "dir_name" --> path to where dss data is located, default =ckts\\opendss-ckts\\IEEE13
    "ckt_name" --> .dss circuit name, default = MasterIEEE13.dss
    "data_path_name" = path to where data will be located once generated from OpenDSS, default = 'ckts\\opendss-ckts\\IEEE13\\data'
    "loc_file" --> name of the coordinate file for grid map, path is the same as the ckt_name, default = 'IEEE13Node_BusXY.csv'
    "plot_snapshot" --> whether to plot or not plot the snapshot results, default = False
    "plot_options" --> id of which quantity to be plotted on the grid map, the list of quantites are  ['voltage', 'current', 'power_real', 'power_imag'], default = 2
    """

    def __init__(self, dir_name='ckts\opendss-ckts\IEEE13',
                 ckt_name='MasterIEEE13_daily.dss', data_path_name='ckts\opendss-ckts\IEEE13\data',
                 loc_file='IEEE13Node_BusXY.csv',
                 plot_snapshot=False,
                 plot_option=2,
                 run_time_series=True,
                 time_series_type='daily',
                 load_shape_file='load_daily.csv'):

        self.print_statements = True
        self.node_names = None
        self.busnames = []
        self.FeederDir = os.path.join(os.getcwd(), dir_name)
        self.MasterFileDir = os.path.join(self.FeederDir, ckt_name)
        self.data_path_name = os.path.join(os.getcwd(), data_path_name)
        self.gridLocFile = os.path.join(self.data_path_name, loc_file)
        self.gridLocFile = r"C:\Users\kini136\OneDrive - PNNL\Desktop\Enhanced_Controls_Dashboard\ckts\opendss-ckts\IEEE13\IEEE13Node_BusXY.csv"
        if os.path.isfile(self.MasterFileDir):
            print(f"Ckt Name Loaded: {self.MasterFileDir}")
            print(f"Directory: {self.FeederDir}")
            print(f"DataPath: {self.data_path_name}")
        else:
            print(f"Wrong path provided for the directory")
#        print("Ckt Loaded" + MasterFileDir + "located at" + FeederDir)

        self.dss_obj = dss

        # self.dss_obj.run_command('Compile ' + self.MasterFileDir)

        self.dss_obj.Basic.DataPath(self.data_path_name)
        self.dss_obj.run_command(f'Compile [{self.MasterFileDir}]')

        # self.dss_obj.run_command('set datapath = ' + self.data_path_name)

        if os.path.isfile(self.gridLocFile):
            print(f"grid loc file {self.gridLocFile}")
            self.dss_obj.run_command(f'BusCoords [{loc_file}]')
            # TODO: read_csv is putting first row as the indices, rather than rows - change that.
            self.grid_xy_data = pd.read_csv(self.gridLocFile, sep=' ')
        else:
            print(f"No grid location points provided")

        grid_map_plot_option_ids = ['voltage', 'current', 'power_real', 'power_imag']

        if plot_snapshot:
            self.snapshot_run(plot_snapshot, grid_map_plot_option_ids[plot_option])

        if run_time_series:
            print(f"Time Series Run Selected with {time_series_type} mode ")
            self.run_time_series(time_series_type=time_series_type, load_shape_file=load_shape_file)


        #self.nodes = np.array(self.dss_obj.Circuit.YNodeOrder())
        #self.num_nodes = self.dss_obj.Circuit.NumNodes()
        #self.get_substation_injections()

        # node voltage information
        #self.get_y_ordered_voltage_array()


    def snapshot_run(self, plot_snapshot, plot_snapshot_id):
        """ Function used for getting the snapshot run result
        """
        print(f"Solving OpenDSS PowerFlow in Snapshot Mode")
        self.dss_obj.run_command('set mode=snap')
        self.dss_obj.run_command('solve')
        print(f"solution converged? {self.dss_obj.Solution.Converged()}")
        print(f"number of iterations took: {self.dss_obj.Solution.Iterations()}")
        if plot_snapshot:
            self.get_bus_branch_data_for_plots()
            print(f"plotting snapshot results")
            self.grid_plot(plot_snapshot_id)
            self.voltage_plot()
        else:
            print(f"Snapshot plot option not selected")

        # self.dss_obj.run_command('Show convergence')
        # self.dss_obj.Solution.Solve()


    def run_time_series(self, time_series_type,
                        load_shape_file):
        #,
#                        node_mons_name,
#                        line_mons_name):
        """

        :param  1) time_series_type
                2) load_shape_file
                3) Nodes to monitor
                4) Line names for monitors
                5)
        :returns:  time series simulation where loads are scaled with the load profile given at the load_shape file
        Following are the steps to do that:
        Add load shape --> self.add_load_shape(time_series_type, load_shape_file)
        Add monitors at loads
        Add voltage regulator monitors
        Add voltage monitors
        Import Monitor Outputs
        Save Results
        """
        # add load_shapes
        self.add_load_shape(time_series_type, load_shape_file)
        # add monitors there is a special order of adding monitors to make it work
        # if voltage monitor is added before load monitor then export monitors don't have the time series
        self.add_load_mons()
        self.add_vreg_mons()
        self.add_branch_mons()
        self.add_sub_mon()
        self.add_volt_mons()

        # Run the model
        print(f"====== Running Time Series Simulation ==========")
        #self.dss_obj.run_command('set controlmode=time')
        self.dss_obj.run_command('set mode=daily')
        self.dss_obj.run_command('set stepsize=1h')
        self.dss_obj.run_command('set number=24')
        self.dss_obj.run_command('solve')
        print(f"time series solution converged? {self.dss_obj.Solution.Converged()}")
        print(f"number of iterations took: {self.dss_obj.Solution.Iterations()}")
        self.rem_mons()
        self.exp_mons()
        self.get_mons_out()


    def rem_mons(self):
        items = []
        csv_items = []
        for item in os.listdir(self.data_path_name):
            if item.endswith(".csv"):
                csv_items.append(item)

        for item in csv_items:
            if "Mon" in item:
                os.remove(os.path.join(self.data_path_name, item))

    def exp_mons(self):
        print(f"========= Exporting Monitors ===========")
        go = self.dss_obj.Monitors.First()
        while go:
            exp_monitor_str = 'export monitors ' + self.dss_obj.Monitors.Name()
            self.dss_obj.Basic.DataPath(self.data_path_name)
            self.dss_obj.run_command(exp_monitor_str)
            go = self.dss_obj.Monitors.Next()

    def get_mons_out(self):

        #TODO: maybe make these np arrays instead of lists
        sens_load_names = []
        sens_load_p = []
        sens_load_q = []
        for load_name in self.dss_obj.Loads.AllNames():
            self.dss_obj.Circuit.SetActiveElement(load_name)
            # current monitored load
            mon_go = self.dss_obj.Monitors.First()
            current_load = 'load.' + load_name
            mon_element_found = []
            while mon_go and not(current_load == self.dss_obj.Monitors.Element()):
                mon_element_found.append(self.dss_obj.Monitors.Element())
                mon_go = self.dss_obj.Monitors.Next()

            if mon_go:
                data = pd.read_csv(self.dss_obj.Monitors.FileName())
                # determine phase offset
                phofs = sum(np.array(self.dss_obj.CktElement.NodeOrder())>0)
                if not(self.dss_obj.Loads.IsDelta()):
                    phofs = phofs + 1
                # process each phase load
                toks = re.sub(r"\..*", "", self.dss_obj.CktElement.BusNames()[0])
                for idx in range(0,sum(self.dss_obj.CktElement.NodeOrder())>0):
                    node = toks + '.' + str(self.dss_obj.CktElement.NodeOrder()[idx])
                    sens_load_names.append(node)
                    vmag = data.iloc[:, 2*idx + 2].values
                    vdeg = data.iloc[:, 2*idx + 3].values
                    imag = data.iloc[:, 2*(phofs+idx)+2].values
                    ideg = data.iloc[:, 2*(phofs+idx)+3].values
                    sens_load_p.append(vmag*imag*np.cos((vdeg-ideg)*np.pi/180))
                    sens_load_q.append(vmag*imag*np.sin((vdeg-ideg)*np.pi/180))
            else:
                print(f"Monitor not found for load:  {current_load}")

        if self.print_statements:
            print(f"Number of Load monitors exported {len(sens_load_p)}")

    # def retrieve_line_monitor_outputs(self):

        sens_line_names = []
        sens_line_Ire = []
        sens_line_Iim = []
        sens_line_Vmag = []

        for line in self.dss_obj.Lines.AllNames():
            # current monitored load
            mon_go = self.dss_obj.Monitors.First()
            current_line = 'line.' + line
            mon_element_found = []
            while mon_go and not(current_line == self.dss_obj.Monitors.Element()):
                mon_element_found.append(self.dss_obj.Monitors.Element())
                mon_go = self.dss_obj.Monitors.Next()

            if mon_go:
                data = pd.read_csv(self.dss_obj.Monitors.FileName())
                # determine phase offset
                # phofs = sum(np.array(self.dss_obj.CktElement.NodeOrder())>0)
                # if not(self.dss_obj.Loads.IsDelta()):
                #     phofs = phofs + 1
                # process each phase load
                toks = re.sub(r"\..*", "", self.dss_obj.CktElement.BusNames()[self.dss_obj.Monitors.Terminal()-1])
                phofs = sum(np.array(self.dss_obj.CktElement.NodeOrder()) > 0)
                for idx in range(0, phofs):
                    node = toks + '.' + str(self.dss_obj.CktElement.NodeOrder()[idx])
                    sens_line_names.append(line+ '.' + str(self.dss_obj.CktElement.NodeOrder()[idx]))
                    vre = data.iloc[:, 2*idx + 2].values
                    vim = data.iloc[:, 2*idx + 3].values
                    sens_line_Vmag.append(np.abs(vre + 1j*vim))
                    sens_line_Ire.append(data.iloc[:, 2*(phofs+idx)+2].values)
                    sens_line_Iim.append(data.iloc[:, 2*(phofs+idx)+3].values)
            else:
                print(f"Monitor not found for line:  {current_line}")

        if self.print_statements:
            print(f"Number of Line monitors exported {len(sens_line_names)}")

        sens_reg_names = []
        sens_reg_taps = []
        sens_reg_primv = []
        sens_reg_regv = []

        sens_xfmr_names_all = []
        go = self.dss_obj.RegControls.First()
        while go:
            xfname = 'transformer.' + str(self.dss_obj.RegControls.Transformer())
            sens_reg_names.append(self.dss_obj.RegControls.Name()+'.'+str(self.dss_obj.CktElement.NodeOrder()[0]))
            # find monitor for this regulator
            mon_go = self.dss_obj.Monitors.First()
            while mon_go:
                if xfname == self.dss_obj.Monitors.Element():
                    data = pd.read_csv(self.dss_obj.Monitors.FileName())
                    sens_xfmr_names_all.append(sens_reg_names)

                    # check for tap ratio monitor
                    if self.dss_obj.Monitors.Mode() == 2:
                        sens_reg_taps.append(data.values)
                    elif self.dss_obj.Monitors.Mode() == 0:
                        tmpVmag = data.iloc[:, 2].values
                        tmpVarg = data.iloc[:, 2].values*np.pi/180
                        vtmp = tmpVmag * (np.cos(tmpVarg) + 1j*np.sin(tmpVarg))
                        if self.dss_obj.Monitors.Terminal() == 1:
                            sens_reg_primv.append(tmpVmag)
                        if self.dss_obj.Monitors.Terminal() == 1:
                            sens_reg_regv.append(tmpVmag)
                    else:
                        print(f"ERROR: unexpected monitor mode for xfrm: {xfname}")
                mon_go = self.dss_obj.Monitors.Next()
            go = self.dss_obj.RegControls.Next()

        if self.print_statements:
            print(f"Number of Regulator monitors exported {len(sens_xfmr_names_all)}")

        sens_sub_names = []
        sens_sub_p = []
        sens_sub_q = []
        source_name_list = []
        go = self.dss_obj.Vsources.First()
        while go:
            sourcename = 'vsource.' + self.dss_obj.Vsources.Name()
            self.dss_obj.Circuit.SetActiveElement(sourcename)

            mon_go = self.dss_obj.Monitors.First()

            while mon_go and not(sourcename == self.dss_obj.Monitors.Element()):
                mon_go = self.dss_obj.Monitors.Next()

            if not(mon_go):
                print(f"ERROR: Could not find monitor for: {sourcename}")

            source_name_list.append(sourcename)
            data = pd.read_csv(self.dss_obj.Monitors.FileName())

            toks = re.sub(r"\..*", "", self.dss_obj.CktElement.BusNames()[0])

            phofs = int(len(self.dss_obj.CktElement.NodeOrder())/len(self.dss_obj.CktElement.BusNames()))
            for idx in range(0, phofs):
                node = toks + '.' + str(self.dss_obj.CktElement.NodeOrder()[idx])
                sens_sub_names.append(node)
                sens_sub_p.append(data.iloc[:, 2*idx + 2].values)
                sens_sub_q.append(data.iloc[:, 2*idx + 3].values)

            go = self.dss_obj.Vsources.Next()

        if self.print_statements:
            print(f"Number of Substation monitors exported: {len(source_name_list)}")

        # exporting node voltages
        node_names = []
        node_voltages = []
        node_voltages_mag = []
        node_mons_list = []
        self.dss_obj.Circuit.SetActiveClass('fault')
        go = self.dss_obj.ActiveClass.First()
        while go:
            faultname = self.dss_obj.CktElement.Name()
            mon_go = self.dss_obj.Monitors.First()
            while mon_go and not(faultname == self.dss_obj.Monitors.Element):
                mon_go = self.dss_obj.Monitors.Next()

            if not(mon_go):
                print(f" ERROR: could not find monitor for: {faultname}")

            node_mons_list.append(faultname)
            data = pd.read_csv(self.dss_obj.Monitors.FileName())
            node_names.append(self.dss_obj.CktElement.BusNames()[0])
            node_voltages.append(data.iloc[:, 2].values + 1j*data.iloc[:, 3].values)
            node_voltages_mag.append(np.sqrt(data.iloc[:, 2].values**2 + data.iloc[:, 3].values**2))

            self.dss_obj.Circuit.SetActiveElement(faultname)
            go = self.dss_obj.ActiveClass.Next()
        if self.print_statements:
            print(f"Number of node monitors exported: {len(node_mons_list)}")

        check_point = 1
    def add_load_shape(self, mode, shape_file):
        """
        function to add load shape
        :param mode:
        :param shape_file:
        :return:
        """
        if mode == 'daily':
            self.shape_file_path =  os.path.join(self.data_path_name, shape_file)

            load_shape_string = 'New Loadshape.dailyshape' \
                                + ' Interval=' + str(1) \
                                + ' npts=' + str(24) \
                                + ' mult=(file=' + self.shape_file_path + ')'
                               # + ' mult=(file=' + shape_file + ')'
            print(f"{load_shape_string}")
            self.dss_obj.run_command(load_shape_string)
        elif mode == 'yearly':
            print(f"Yearly Mode has not yet been setup")
#            self.load_vals = pd.read_csv(self.shape_path)

    def add_load_mons(self):
        mons_nodes = ['634.1', '634.2', '634.3', '675.1', '675.2', '675.3', '611.3', '652.1']
        print(f"====Editing Loads and Adding Monitors to its Selected Nodes====")
        # numloads = len(self.dss_obj.Loads.AllNames())
        mon_to_load_str_all = []
        load_edit_str_all = []
        print(f"total loads: {len(self.dss_obj.Loads.AllNames())}")
        #print(*self.dss_obj.Loads.AllNames(),sep="\n")
        for load_name in self.dss_obj.Loads.AllNames():
            #shape_name = 'shape_' + load
            load_edit_string = 'edit load.' + load_name + ' daily=dailyshape'
            load_edit_str_all.append(load_edit_string)
            # print(f"{load_edit_string}")
            self.dss_obj.run_command(load_edit_string)

            self.dss_obj.Circuit.SetActiveElement('Load.' + load_name)
            bus = re.sub(r"\..*", "", self.dss_obj.CktElement.BusNames()[0])
            if any(bus in nodes for nodes in mons_nodes):
                mon_to_load_str = 'new monitor.' \
                                  + 'load_VI_' + load_name \
                                  + ' element=' + 'load.' + load_name\
                                  + ' terminal=' + str(1) \
                                  + ' mode=' + str(0) \
                                  + ' VIPolar=true'
                #print(f"{mon_to_load_str}")
                self.dss_obj.run_command(mon_to_load_str)
                mon_to_load_str_all.append(mon_to_load_str)
        mons_nodes_asked = len(mons_nodes)
        mons_nodes_placed = len(mon_to_load_str_all)

        if self.print_statements:
            print(*load_edit_str_all, sep="\n")
            print(*mon_to_load_str_all, sep="\n")
            print(f"Monitor Nodes Specified {mons_nodes_asked}")
            print(f"Monitor Nodes Placed {mons_nodes_placed}")
            # print(f"{load_edit_str_all}")
            # print(f"{mon_to_load_str_all}")

    def add_vreg_mons(self):
        """
        Add monitors for 1) secondary, 2) primary sides of regulators and 3) and taps
        :return:
        """
        go = self.dss_obj.RegControls.First()
        while go:
            xfrmr_name = self.dss_obj.RegControls.Transformer()
            # monitor for taps
            mon_tap_str = 'new monitor.' + \
                          'reg_tap_' + xfrmr_name + \
                          ' element=' + 'transformer.' + xfrmr_name + \
                          ' terminal=' + str(2) + \
                          ' mode=' + str(2)
            # monitor for primary voltage
            mon_prim_str = 'new monitor.' + \
                          'reg_primv_' + xfrmr_name + \
                          ' element=' + 'transformer.' + xfrmr_name + \
                          ' terminal=' + str(1) + \
                          ' mode=' + str(0)
            # monitor for regulators
            mon_reg_str = 'new monitor.' + \
                          'reg_regv_' + xfrmr_name + \
                          ' element=' + 'transformer.' + xfrmr_name + \
                          ' terminal=' + str(2) + \
                          ' mode=' + str(0)
            if self.print_statements:
                print(f"{mon_tap_str}")
                print(f"{mon_prim_str}")
                print(f"{mon_reg_str}")

            self.dss_obj.run_command(mon_tap_str)
            self.dss_obj.run_command(mon_prim_str)
            self.dss_obj.run_command(mon_reg_str)

            go = self.dss_obj.RegControls.Next()

    def add_branch_mons(self):
        mon_lines = ['650632', '632633', '671684']
        mon_lines_str_all = []
        for Line in self.dss_obj.Lines.AllNames():
            if any(Line in lines for lines in mon_lines):
                mon_to_line_str = 'new monitor.' \
                                  + 'line_VI_' + Line \
                                  + ' element=' + 'line.' + Line \
                                  + ' terminal=' + str(1) \
                                  + ' mode=' + str(0)  \
                                  + ' VIPolar=false'
                self.dss_obj.run_command(mon_to_line_str)
                mon_lines_str_all.append(mon_to_line_str)
        if self.print_statements:
            print(*mon_lines_str_all, sep="\n")
            print(f"Monitor Lines Specified {len(mon_lines)}")
            print(f"Monitor Nodes Placed {len(mon_lines_str_all)}")

    def add_sub_mon(self):

        mon_to_sub_str = 'new monitor.sub' \
                          + ' element=' + 'vsource.source' \
                          + ' terminal=' + str(1) \
                          + ' mode=' + str(1) \
                          + ' ppolar=false'
        self.dss_obj.run_command(mon_to_sub_str)

        print(f"==== Adding Substation Monitor =======")
        print(f"{mon_to_sub_str}")

    def add_volt_mons(self):
        """
        add voltage monitors to all buses using a fault stub
        :return:
        """
        self.node_names = np.array("                      ").repeat(self.dss_obj.Circuit.NumNodes())
        i = 0
        fault_str_all = []
        volt_mon_str_all = []
        for busname in self.dss_obj.Circuit.AllBusNames():
            self.busnames.append(busname)
            self.dss_obj.Circuit.SetActiveBus(busname)
            for phase in self.dss_obj.Bus.Nodes():
                self.node_names[i] = busname + '.' + str(phase)
                # add a loadless load to this node
                stub_name = busname + '_' + str(phase) + '_stub'
                fault_str = 'new fault.'  \
                            + stub_name + ' phases=1' \
                            + ' bus1=' + self.node_names[i] \
                            + ' enabled=false'
                fault_str_all.append(fault_str)
                self.dss_obj.run_command(fault_str)
                volt_mon_str = 'new monitor.nodev_' + busname + '_' + str(phase) \
                               + ' element=' + 'fault.' + stub_name \
                               + ' terminal=1'\
                               + ' mode=0' \
                               + ' VIPolar=false'
                volt_mon_str_all.append(volt_mon_str)
                self.dss_obj.run_command(volt_mon_str)
        if self.print_statements:
            print(f"Total nodes in the network: {self.dss_obj.Circuit.NumNodes()}")
            print(f"Total voltage monitors placed: {len(volt_mon_str_all)}")
            print(*fault_str_all, sep="\n")
            print(*volt_mon_str_all, sep="\n")

            i += 1


    # def export_monitors(self):

    def get_substation_injections(self):
        """ Function used for extracting power injection information at only slack bus from OpenDSS model
        """
        #TODO: make this dictionary of the size of substation source bus, instead of whole node
        Nodes = self.nodes
        self.s0 = pd.DataFrame(np.complex_(0), index=Nodes, columns=['s0'])
        for Source in self.dss_obj.Vsources.AllNames():
            self.dss_obj.Circuit.SetActiveElement('Vsource.' + Source)
            self.s0.s0['SOURCEBUS' + '.1'] = -(
                    self.dss_obj.CktElement.Powers()[0] + np.multiply(1j, self.dss_obj.CktElement.Powers()[1]))
            self.s0.s0['SOURCEBUS' + '.2'] = -(
                    self.dss_obj.CktElement.Powers()[2] + np.multiply(1j, self.dss_obj.CktElement.Powers()[3]))
            self.s0.s0['SOURCEBUS' + '.3'] = -(
                    self.dss_obj.CktElement.Powers()[4] + np.multiply(1j, self.dss_obj.CktElement.Powers()[5]))
        # print(self.s0)
    def get_y_ordered_voltage_array(self):
        """
        Function used for extracting Voltage phasor information at all nodes from OpenDSS model
        The order of voltage is similar to what Y-bus uses
        I = Y*V
        """
        Vol = self.dss_obj.Circuit.YNodeVArray()
        V_real = np.array([Vol[i] for i in range(len(Vol)) if i % 2 == 0])
        V_imag = np.array([Vol[i] for i in range(len(Vol)) if i % 2 == 1])
        self.voltages = V_real + np.multiply(1j, V_imag)
        self.v0 = self.voltages[0:3]
        self.vL = self.voltages[3:]
        # print(self.vL)



    def get_bus_branch_data_for_plots(self):
        """
        this function calls bus_data_input_for plots and branch_data_for_plot, so that they are not called in a wrong order
        """
        self.bus_data_input_for_plot()

        self.branch_data_for_plot()


    def bus_data_input_for_plot(self):
        """
        Function to extract bus information, its x/y axis coordinates, voltages, distance from the feeder
            name - string - bus name
            V - complex array (n x 3) - node bus voltage
            distance - array (n) - distance from the energymeter
            x - array (n) - from-bus x location
            y - array (n) - from-bus y location
        """
        # Bus Extraction
        # make the x,y, distance, and voltage numpy arrays of length n and set
        # the values to all zeros
        # note:  the voltage array is an array of complex values
        n = self.dss_obj.Circuit.NumBuses()
        x = np.zeros(n)
        y = np.zeros(n)
        distance = np.zeros(n)
        V = np.zeros((n, 3), dtype=complex)
        name = np.array("                                ").repeat(n)
        kVBase = np.zeros(n)
        bus_nodes = []
        # populate the arrays by looking at the each bus in turn from 0 to n
        # note:  by convention all arrays are zero-based in python
        bnames = self.dss_obj.Circuit.AllBusNames()
        for i in range(0, n):
            self.dss_obj.Circuit.SetActiveBus(bnames[i])
            name[i] = self.dss_obj.Bus.Name()
            x[i] = self.dss_obj.Bus.X()
            y[i] = self.dss_obj.Bus.Y()
            distance[i] = self.dss_obj.Bus.Distance()
            v = np.array(self.dss_obj.Bus.Voltages())
            nodes = np.array(self.dss_obj.Bus.Nodes())
            kVBase[i] = np.array(self.dss_obj.Bus.kVBase())
            # we're only interested in the first three nodes
            # (also called terminals) on the bus
            if nodes.size > 3: nodes = nodes[0:3]
            cidx = 2 * np.array(range(0, int(min(v.size / 2, 3))))
            V[i, nodes - 1] = v[cidx] + 1j * v[cidx + 1]
            bus_nodes.append(nodes)
        self.bus_data = {'Name': name, 'Voltages': V, 'X': x, 'Y': y, 'Distance': distance, 'Nodes': bus_nodes, "kVBase": kVBase}

        # self.bus_data = pd.DataFrame(bdata)
        # print(self.bus_data)

        check = 1
        # df = pd.DataFrame(data=data, index=rows, columns=columns)


    def branch_data_for_plot(self):
        """
        Function to extract branch information, to be utilized for the plots
            name - string - branch name
            busname - string (n) - from-node bus name
            busnameto - string (n) - to-node bus name
            V - complex array (n x 3) - from-node bus voltage
            Vto - complex array (n x 3) - to-node bus voltage
            I - complex array (n x 3) - branch currents
            nphases - array (n) - number of phases
            distance - array (n) - distance from the energy meter
            x - array (n) - from-bus x location
            y - array (n) - from-bus y location
            xto - array (n) - to-bus x location
            yto - array (n) - to-bus y location
        """
        n = np.size(self.dss_obj.Lines.AllNames())
        busname = np.array("                      ").repeat(n)
        busnameto = np.array("                      ").repeat(n)
        x = np.zeros(n)
        y = np.zeros(n)
        xto = np.zeros(n)
        yto = np.zeros(n)
        distance = np.zeros(n)
        nphases = np.zeros(n)
        kvbase = np.zeros(n)
        I = np.zeros((n, 3), dtype=complex)
        V = np.zeros((n, 3), dtype=complex)
        Vto = np.zeros((n, 3), dtype=complex)
        P = np.zeros((n, 3))
        Q = np.zeros((n, 3))
        linename = np.array("                      ").repeat(n)
        i = 0
        for Line in self.dss_obj.Lines.AllNames():
            linename[i] = Line
            self.dss_obj.Circuit.SetActiveElement('Line.' + Line)
            # bus1.append(self.dss_obj.CktElement.BusNames()[0])
            busnameto[i]  = re.sub(r"\..*", "", self.dss_obj.CktElement.BusNames()[1])
            bus_idto = self.bus_data["Name"].tolist().index(busnameto[i])

            # check whether bus has the x,y data defined, if not, then go ahead
            try:
                xto[i] = self.bus_data["X"][bus_idto]
                yto[i] = self.bus_data["Y"][bus_idto]
            except IndexError:
                xto[i] = []
                yto[i] = []
                continue


            #if self.bus_data["X"][bus_idto] == 0 or self.bus_data["Y"][bus_idto] == 0: continue
            distance[i] = self.bus_data["Distance"][bus_idto]
            v = self.bus_data["Voltages"][bus_idto]
            nodes = np.array( self.bus_data["Nodes"][bus_idto])
            kvbase[i] = self.bus_data["kVBase"][bus_idto]
            nphases[i] = nodes.size
            if nodes.size > 3: nodes = nodes[0:3]
            cidx = 2 * np.array(range(0, int(min(v.size / 2, 3))))
            Vto[i, nodes-1] = v[nodes-1]#v[cidx] + 1j * v[cidx + 1]

            busname[i]  = re.sub(r"\..*", "", self.dss_obj.CktElement.BusNames()[0])
            bus_id = self.bus_data["Name"].tolist().index(busname[i])

            try:
                x[i] = self.bus_data["X"][bus_id]
                y[i] = self.bus_data["Y"][bus_id]
            except IndexError:
                x[i] = []
                y[i] = []
                continue

            # x[i] = self.bus_data["X"][bus_id]
            # y[i] = self.bus_data["Y"][bus_id]
            #if self.bus_data["X"][bus_id] == 0 or self.bus_data["Y"][bus_id] == 0: continue # skip lines without proper bus coordinates

            v = self.bus_data["Voltages"][bus_id]

            V[i, nodes-1] = v[nodes-1]#v[cidx] + 1j * v[cidx + 1]
            current = np.array(self.dss_obj.CktElement.Currents())
            I[i, nodes-1] = current[np.arange(0,len(nodes)*2,2)] + 1j*current[np.arange(0,len(nodes)*2,2)+1]
            P[i, nodes-1] = np.real(V[i, nodes-1]*np.conj(I[i, nodes-1]))
            Q[i, nodes-1] = np.imag(V[i, nodes-1]*np.conj(I[i, nodes-1]))
            i = i + 1
        self.branch_data = {'Name': linename[0:i],
                            'BusTo': busnameto[0:i],
                            'BusFrom': busname[0:i],
                            'nPhases': nphases[0:i],
                            'kVBase': kvbase[0:i],
                            'x': x[0:i],
                            'xto': xto[0:i],
                            'y': y[0:i],
                            'yto': yto[0:i],
                            'Distance': distance[0:i],
                            "VoltageTo": Vto[0:i],
                            "VoltageFrom": V[0:i],
                            "Current": I[0:i],
                            "power_real": P[0:i],
                            "power_imag": Q[0:i]}
        #print(self.branch_data)


    def voltage_plot(self):
        """
            Function to plot OpenDSS voltages as a function of feeder distances
        """
        v_min = 0.95 * np.ones(len(self.branch_data['Name']))
        v_max = 1.05 * np.ones(len(self.branch_data['Name']))



        #get distance ids in acending order
        idx = np.argsort(self.branch_data['Distance'])
        # collect voltages
        v_a = np.abs(self.branch_data['VoltageFrom'][idx, 0])/ (self.branch_data['kVBase'][idx] * 1e3)
        v_b = np.abs(self.branch_data['VoltageFrom'][idx, 1])/ (self.branch_data['kVBase'][idx] * 1e3)
        v_c = np.abs(self.branch_data['VoltageFrom'][idx, 2])/ (self.branch_data['kVBase'][idx] * 1e3)

        # y_a = np.abs(self.branch_data['VoltageFrom'])[:, 0] / (self.branch_data['kVBase'] * 1e3)
        # y_b = np.abs(self.branch_data['VoltageFrom'])[:, 1] / (self.branch_data['kVBase'] * 1e3)
        # y_c = np.abs(self.branch_data['VoltageFrom'])[:, 2] / (self.branch_data['kVBase'] * 1e3)

        #sort the distances
        x = self.branch_data['Distance'][idx]

        x_a = x[v_a > 0.0]
        v_a = v_a[v_a > 0.0]
        x_b = x[v_b > 0.0]
        v_b = v_b[v_b > 0.0]
        x_c = x[v_c > 0.0]
        v_c = v_c[v_c > 0.0]
        fig, ax = plt.subplots()
        ax.scatter(x_a, v_a, label='phase a', c="g")
        ax.plot(x_a, v_a, c="g")
        ax.scatter(x_b, v_b, label='phase b', c="r")
        ax.plot(x_b, v_b, c="r")
        ax.scatter(x_c, v_c, label='phase c', c="b")
        ax.plot(x_c, v_c, c="b")
        ax.plot(x, v_min, color='k')
        ax.plot(x, v_max, color='k')
        ax.set_xlabel('Distance from Feeder')
        ax.set_ylabel('(per unit)')
        ax.legend()
        plt.show()


    def grid_plot(self, option='voltage'):
        """
            Function to plot DSS grid map with similar to OPENDSS format:
        """
        # def add_edge_to_graph(G, e1, e2, w):
        #     G.add_edge(e1, e2, weight=w)
        #
        # def add_node_to_graph(G, n, pos):
        #     G.add_node(n, pos=pos)

        # ------------------- For reference: sample code for adding nodes to graph
        # G = nx.Graph()
        # node_label = ['b1', 'b2', 'b3', 'b4', 'b5']
        # points = [(200.0, 200.0), (200.0, 150.0), (300.0, 150.0), (150.0, 150.0), (200.0, 100.0)]
        # edges = [(0, 1, 10), (1, 2, 10), (1, 3, 10), (1, 4, 10)]
        #
        # for i in range(len(edges)):
        #     # add_edge_to_graph(G, points[edges[i][0]], points[edges[i][1]], edges[i][2])
        #     add_edge_to_graph(G, node_label[edges[i][0]], node_label[edges[i][1]], edges[i][2])
        # for i in range(len(node_label)):
        #     add_node_to_graph(G, node_label[i], points[i])
        # # pos = {point: point for point in points}
        # pos = nx.get_node_attributes(G, 'pos')
        # # add axis
        # fig, ax = plt.subplots()
        # nx.draw(G, pos=pos, node_color='k', ax=ax, with_labels=True)
        # nx.draw(G, pos=pos, node_size=1500, ax=ax, with_labels=True)  # draw nodes and edges
        #nx.draw_networkx_labels(G, pos=pos)  # draw node labels/names
        #nx.draw_networkx_nodes(G, pos=pos, label=node_label)
        # draw edge weights
        # labels = nx.get_edge_attributes(G, 'weight')
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)
        # plt.axis("on")
        #ax.set_xlim(0, 11)
        #ax.set_ylim(0, 11)
        #ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        # plt.show()

        if option == 'voltage':
            weight = 'VoltageFrom'
            title_text = 'Voltage Across Network'
            weight_val = np.mean(np.abs(self.branch_data[weight]), axis=1) # we just have one edge representing multiphases, so using something simple
        elif option == 'current':
            weight = 'Current'
            title_text = 'Current Across Network'
            weight_val = np.mean(np.abs(self.branch_data[weight]), axis=1) # we just have one edge representing multiphases, so using something simple

        elif option == 'power_real':
            weight = 'power_real'
            title_text = 'Real Power Across Network'
            weight_val = np.sum(self.branch_data[weight], axis=1)
        elif option == 'power_imag':
            weight = 'power_imag'
            title_text = 'Reactive Power Across Network'
            weight_val = np.sum(self.branch_data[weight], axis=1)
        else:
            weight = 'VoltageFrom'
            title_text = 'Voltage Across Network'
            weight_val = np.mean(np.abs(self.branch_data[weight]), axis=1) # we just have one edge representing multiphases, so using something simple

        G = nx.Graph()

        for i in range(len(self.branch_data['Name'])):
            G.add_edge(self.branch_data['BusFrom'][i], self.branch_data['BusTo'][i], weight = weight_val[i])
            x1 = self.bus_data['X'][self.bus_data['Name'].tolist().index(self.branch_data['BusFrom'][i])]
            y1 = self.bus_data['Y'][self.bus_data['Name'].tolist().index(self.branch_data['BusFrom'][i])]
            G.add_node(self.branch_data['BusFrom'][i], pos=(x1, y1))
            x2 = self.bus_data['X'][self.bus_data['Name'].tolist().index(self.branch_data['BusTo'][i])]
            y2 = self.bus_data['Y'][self.bus_data['Name'].tolist().index(self.branch_data['BusTo'][i])]
            G.add_node(self.branch_data['BusTo'][i], pos=(x2, y2))
        pos = nx.get_node_attributes(G, 'pos')



        fig, ax = plt.subplots()

        nodes = nx.draw_networkx_nodes(G, pos=pos, node_color="indigo")
        edges = nx.draw_networkx_edges(G, pos=pos, edge_color=weight_val, width=4,
                                       edge_cmap=plt.cm.Blues)
        fig.colorbar(edges)
        plt.axis('off')
        ax.set_title(title_text)
        plt.show()



if __name__ == "__main__":
    # FeederDir = os.path.join(os.getcwd(), '..\ckts\opendss-ckts\IEEE13')
    # MasterFileDir = os.path.join(FeederDir, 'IEEE13Nodeckt.dss')
    # print(MasterFileDir)
    # print(FeederDir)

    # dir_name = 'ckts\\opendss-ckts\\IEEE13',
    # ckt_name = 'MasterIEEE13_daily.dss', data_path_name = 'ckts\\opendss-ckts\\IEEE13\\data',
    # loc_file = 'IEEE13Node_BusXY.csv',
    # plot_snapshot = False,
    # plot_option = 2,
    # run_time_series = True,
    # time_series_type = 'daily',
    # load_shape_file = 'load_daily.csv':

    general_setting = {
        "dir_name": "ckts\\opendss-ckts\\IEEE13",
        "ckt_name": "MasterIEEE13_daily.dss",
        "data_path_name": "ckts\\opendss-ckts\\IEEE13\\data",
        "loc_file": 'IEEE13Node_BusXY.csv',
        "snapshot_run": True,
        "time_series_run": True,
    }
    time_series_settings = {
        "time_serties_type": "daily",
        "load_shape_file": "load_daily.csv",
        "mons_nodes": ['634.1', '634.2', '634.3', '675.1', '675.2', '675.3', '611.3', '652.1'],
        "mons_lines": ['Line.650632', 'Line.632633', 'Line.671684'],
    }

    # coord_file = "IEEE13Node_BusXY.csv"

    utils = dss_utils(plot_snapshot=True)
    # utils.snapshot_run()
    utils.get_y_ordered_voltage_array()
    #utils.bus_data_input_for_plot()

    #utils.branch_data_for_plot()



    #TODO: Add function for adding battery point, charge/discharge level