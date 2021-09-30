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
import re
import networkx as nx

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



        self.dss_obj = dss

        # print(FeederDir)

        self.dss_obj.run_command('set datapath = ' + self.data_path_name)
        self.dss_obj.run_command('Compile ' + self.MasterFileDir)

        if os.path.isfile(self.gridLocFile):
            self.dss_obj.run_command('BusCoords ' + loc_file)
            # TODO: read_csv is putting first row as the indices, rather than rows - change that.
            self.grid_xy_data = pd.read_csv(self.gridLocFile)
        else:
            print(f"No grid location points provided")

        self.snapshot_run()
        # self.dss_obj.run_command('set mode=snap')
        # self.dss_obj.run_command('solve')
        self.nodes = np.array(self.dss_obj.Circuit.YNodeOrder())
        self.num_nodes = self.dss_obj.Circuit.NumNodes()
        self.substation_injections()

        # node voltage information
        self.y_ordered_voltage_array()

        #
        # self.dss_obj.ActiveCircuit
        self.plot_grid_dss()

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
        linename = np.array("                      ").repeat(n)
        i = 0
        for Line in self.dss_obj.Lines.AllNames():
            linename[i] = Line
            self.dss_obj.Circuit.SetActiveElement('Line.' + Line)
            # bus1.append(self.dss_obj.CktElement.BusNames()[0])
            busnameto[i]  = re.sub(r"\..*", "", self.dss_obj.CktElement.BusNames()[1])
            bus_idto = self.bus_data["Name"].tolist().index(busnameto[i])
            xto[i] = self.bus_data["X"][bus_idto]
            yto[i] = self.bus_data["Y"][bus_idto]
            if self.bus_data["X"][bus_idto] == 0 or self.bus_data["Y"][bus_idto] == 0: continue
            distance[i] = self.bus_data["Distance"][bus_idto]
            v = self.bus_data["Voltages"][bus_idto]
            nodes = np.array( self.bus_data["Nodes"][bus_idto])
            kvbase[i] = self.bus_data["kVBase"][bus_idto]
            nphases[i] = nodes.size
            if nodes.size > 3: nodes = nodes[0:3]
            cidx = 2 * np.array(range(0, int(min(v.size / 2, 3))))
            Vto[i, nodes-1] = v[cidx] + 1j * v[cidx + 1]

            busname[i]  = re.sub(r"\..*", "", self.dss_obj.CktElement.BusNames()[0])
            bus_id = self.bus_data["Name"].tolist().index(busname[i])
            x[i] = self.bus_data["X"][bus_id]
            y[i] = self.bus_data["Y"][bus_id]
            if self.bus_data["X"][bus_id] == 0 or self.bus_data["Y"][bus_id] == 0: continue # skip lines without proper bus coordinates

            v = self.bus_data["Voltages"][bus_id]

            V[i, nodes-1] = v[cidx] + 1j * v[cidx + 1]
            current = np.array(self.dss_obj.CktElement.Currents())
            I[i, nodes-1] = current[cidx] + 1j * current[cidx + 1]
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
                            "Current": I[0:i]}
        print(self.branch_data)


    def plot_grid_dss(self):

        """
            Function to plot DSS results:
            First it inputs the coordinates information for buses
            Bus and Branch Creation are the Dssdirect version of dssvlplot in
            OpenDSS github python example

        """

        def voltage_plot(self):
            """
                Function to plot OpenDSS voltages
            """
            v_min = 0.95 * np.ones(len(self.bus_data['Name']))
            v_max = 1.05 * np.ones(len(self.bus_data['Name']))

            x = self.bus_data['Distance']
            y_a = np.abs(self.bus_data['Voltages'])[:, 0] / (self.bus_data['kVBase'] * 1e3)
            y_b = np.abs(self.bus_data['Voltages'])[:, 1] / (self.bus_data['kVBase'] * 1e3)
            y_c = np.abs(self.bus_data['Voltages'])[:, 2] / (self.bus_data['kVBase'] * 1e3)
            x_a = x[y_a > 0.0]
            y_a = y_a[y_a > 0.0]
            x_b = x[y_b > 0.0]
            y_b = y_b[y_b > 0.0]
            x_c = x[y_c > 0.0]
            y_c = y_c[y_c > 0.0]
            fig, ax = plt.subplots()
            ax.scatter(x_a, y_a, label='phase a')
            ax.scatter(x_b, y_b, label='phase b')
            ax.scatter(x_c, y_c, label='phase c')
            ax.plot(x, v_min, color='k')
            ax.plot(x, v_max, color='k')
            ax.set_xlabel('Distance from Feeder')
            ax.set_ylabel('(per unit)')
            ax.legend()




        def map_plot(self):
            """
                Function to plot DSS grid map with similar to OPENDSS format:
            """
            # TODO: scale the edges using
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
            G = nx.Graph()

            for i in range(len(self.branch_data['Name'])):
                G.add_edge(self.branch_data['BusFrom'][i], self.branch_data['BusTo'][i])
                x1 = self.bus_data['X'][self.bus_data['Name'].tolist().index(self.branch_data['BusFrom'][i])]
                y1 = self.bus_data['Y'][self.bus_data['Name'].tolist().index(self.branch_data['BusFrom'][i])]
                G.add_node(self.branch_data['BusFrom'][i], pos=(x1, y1))
                x2 = self.bus_data['X'][self.bus_data['Name'].tolist().index(self.branch_data['BusTo'][i])]
                y2 = self.bus_data['Y'][self.bus_data['Name'].tolist().index(self.branch_data['BusTo'][i])]
                G.add_node(self.branch_data['BusTo'][i], pos=(x2, y2))
            pos = nx.get_node_attributes(G, 'pos')
            fig, ax = plt.subplots()
            nx.draw(G, pos=pos, node_color='k', ax=ax, with_labels=True)
            nx.draw(G, pos=pos, node_size=500, ax=ax, with_labels=True)  # draw nodes and edges

            ax.set_xlim(min(min(self.branch_data["xto"]),min(self.branch_data["x"]))-10, max(max(self.branch_data["xto"]),max(self.branch_data["x"]))+10)
            ax.set_ylim(min(min(self.branch_data["yto"]),min(self.branch_data["y"]))-10, max(max(self.branch_data["yto"]),max(self.branch_data["y"]))+10)
            ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

            plt.show()



        self.bus_data_input_for_plot()
        # self.bus_data_input()

        self.branch_data_for_plot()

        # bp = 1
        map_plot(self)
        voltage_plot(self)

if __name__ == "__main__":
    # FeederDir = os.path.join(os.getcwd(), '..\ckts\opendss-ckts\IEEE13')
    # MasterFileDir = os.path.join(FeederDir, 'IEEE13Nodeckt.dss')
    # print(MasterFileDir)
    # print(FeederDir)
    coord_file = "IEEE13Node_BusXY.csv"
    utils = dss_utils()
    # utils.snapshot_run()
    utils.y_ordered_voltage_array()
