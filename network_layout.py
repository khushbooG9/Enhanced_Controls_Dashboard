import dash_html_components as html
import dash_core_components as dcc
from components.common import common_graph, common_slider, common_switch


def build_network_tab():
    """
    Function to put together the settings tab
    """
    return html.Div(
        className="network-container",
        id="network-container",
        children=[network_left_panel(), network_right_panel()],
    )


# --- left panel ---
def network_left_panel():
    """
    Function to generate a panel on left side
    """

    return html.Div(
        id="network-left-page",
        className="network-left-page",
        children=[build_network_controls(), build_bottom_left_panel()],
    )

def build_network_controls():
    """
    Function to generate a panel for network on left side
    """
    return html.Div(
        id="network-model-panel",
        className="network-model-panel",
        children=[
            html.Label("Network Model"),
        ],
    )


def build_bottom_left_panel():
    """
    Function to build bottom panel for graph placeholder
    """
    return html.Div(
        id="network-bottom-left-section-container",
        className="network-graph-container",
        children=[
            html.Label("Plot 2"),
            common_graph(id="network-bottom-left-graph"),
        ],
    )
# --- left panel ---


# --- right panel ---
def network_right_panel():
    """
    Function to generate a panel on right side
    """

    return html.Div(
        id="network-right-page",
        className="network-right-page",
        children=[build_top_right_panel(), build_bottom_right_panel()],
    )



def build_top_right_panel():
    """
    Function to build top panel for graph placeholder
    """

    return html.Div(
        id="network-top-right-section-container",
        className="network-graph-container",
        children=[
            html.Label("Plot 1"),
            common_graph(id="network-top-right-graph"),
        ],
    )


def build_bottom_right_panel():
    """
    Function to build bottom panel for graph placeholder
    """
    return html.Div(
        id="network-bottom-right-section-container",
        className="network-graph-container",
        children=[
            html.Label("Plot 3"),
            common_graph(id="network-bottom-right-graph"),
        ],
    )
# --- right panel ---
