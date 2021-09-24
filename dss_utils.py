import opendssdirect as dss
import os
from scipy.sparse import csc_matrix, linalg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class dss_utils:
    """
    Class to collect useful opendss utilities using opendssdirect package
    """

    def __init__(self, dir_name='ckts\\opendss-ckts\\IEEE13', ckt_name='MasterIEEE13.dss', data_path_name='ckts\\opendss-ckts\\IEEE13\\data',loc_file='IEEE13Node_BusXY.csv'):
        "initialize the ckt with its name and directory name"

        self.FeederDir = os.path.join(os.getcwd(), dir_name)
        self.MasterFileDir = os.path.join(self.FeederDir, ckt_name)
        self.data_path_name = os.path.join(os.getcwd(), data_path_name)
        self.gridLocFile = os.path.join(self.FeederDir, loc_file)
        if os.path.isfile(self.MasterFileDir):
            print(f"Ckt Name Loaded: {self.MasterFileDir}")
            print(f"Directory: {self.FeederDir}")
            print(f"DataPath: {self.data_path_name}")
        else:
            print(f"Wrong path provided for the directory")
#        print("Ckt Loaded" + MasterFileDir + "located at" + FeederDir)

        if os.path.isfile(self.gridLocFile):
            #TODO: read_csv is putting first row as the indices, rather than rows - change that.
            self.grid_xy_data = pd.read_csv(self.gridLocFile)
        else:
            print(f"No grid location points provided")

        # print(FeederDir)

        self.dss_obj = dss
        self.dss_obj.run_command('set datapath = ' + self.data_path_name)
        self.dss_obj.run_command('Compile ' + self.MasterFileDir)
        self.snapshot_run()
        # self.dss_obj.run_command('set mode=snap')
        # self.dss_obj.run_command('solve')
        self.nodes = np.array(self.dss_obj.Circuit.YNodeOrder())
        self.num_nodes = self.dss_obj.Circuit.NumNodes()
        self.substation_injections()

        # node information
        self.y_ordered_voltage_array()

        #

    def snapshot_run(self):
        """ Function used for getting the snapshot run result
        """
        print(f"Solving OpenDSS PowerFlow in Snapshot Mode")
        self.dss_obj.run_command('set mode=snap')
        self.dss_obj.run_command('solve')
        print(f"solution converged? {self.dss_obj.Solution.Converged()}")
        print(f"number of iterations took: {self.dss_obj.Solution.Iterations()}")
        # self.dss_obj.run_command('Show convergence')
        # self.dss_obj.Solution.Solve()

    def substation_injections(self):
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
    def y_ordered_voltage_array(self):
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

    def plot_grid_dss(self):

        """
            Function to plot DSS results:

        """
        # bus_name = self.grid_xy_data[ ,:0]
        # x = self.grid_xy_data[, :1]
        # y = self.grid_xy_data[,: 2]

        # plt.plot(x,y)
        # text = 1

if __name__ == "__main__":
    # FeederDir = os.path.join(os.getcwd(), '..\ckts\opendss-ckts\IEEE13')
    # MasterFileDir = os.path.join(FeederDir, 'IEEE13Nodeckt.dss')
    # print(MasterFileDir)
    # print(FeederDir)
    coord_file = "IEEE13Node_BusXY.csv"
    utils = dss_utils()
    # utils.snapshot_run()
    utils.y_ordered_voltage_array()
