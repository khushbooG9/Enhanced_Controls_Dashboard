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
        print(self.branch_data)


    def plot_grid_dss(self):

        """
            Function to plot DSS results:
            First it inputs the coordinates information for buses
            Bus and Branch Creation are the Dssdirect version of dssvlplot in
            OpenDSS github python example

        """
        #TODO: check voltage profile, if they are accurate
        def voltage_plot(self):
            """
                Function to plot OpenDSS voltages
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


            # number_of_edges = G.number_of_edges()
            # edge_colors = range(2, number_of_edges + 2)
            # edge_alphas = [(5 + i) / (number_of_edges + 4) for i in range(number_of_edges)]
            # cmap = plt.cm.plasma
            #colors = 2 + 2*weight_val/max(weight_val)

            fig, ax = plt.subplots()

            nodes = nx.draw_networkx_nodes(G, pos=pos, node_color="indigo")
            edges = nx.draw_networkx_edges(G, pos=pos, edge_color=weight_val, width=4,
                                           edge_cmap=plt.cm.Blues)
            fig.colorbar(edges)
            plt.axis('off')
            ax.set_title(title_text)
            plt.show()

            # edges = nx.draw_networkx_edges(G, pos, edge_color=edge_colors, edge_cmap=cmap, width=2)
            # print(str(number_of_edges))
            # print(str(edge_alphas))

            # for i in range(number_of_edges):
            #     edges[i].set_alpha(edge_alphas[i])
            # pc = mpl.collections.PatchCollection(edges, cmap=cmap)
            # pc.set_array(edge_colors)
            # plt.colorbar(pc)
            #
            # ax = plt.gca()
            # ax.set_axis_off()
            # plt.show()
            # nx.draw(G, pos=pos, node_color="indigo", ax=ax, with_labels=True)
            # nx.draw(G, pos=pos, node_size=200, ax=ax, with_labels=True)  # draw nodes and edges

            # ax.set_xlim(min(min(self.branch_data["xto"]),min(self.branch_data["x"]))-10, max(max(self.branch_data["xto"]),max(self.branch_data["x"]))+10)
            # ax.set_ylim(min(min(self.branch_data["yto"]),min(self.branch_data["y"]))-10, max(max(self.branch_data["yto"]),max(self.branch_data["y"]))+10)
            # ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
            # ax.set_title(title_text)



        self.bus_data_input_for_plot()
        # self.bus_data_input()

        self.branch_data_for_plot()

        plot_options = ['voltage', 'current', 'power_real', 'power_imag']

        grid_plot(self, plot_options[2])
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
    #TODO: Add function for adding battery point, charge/discharge level