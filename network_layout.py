import dash_html_components as html


def build_network_tab():
    """
    Function to put together the settings tab
    """
    return html.Div(
        className="network-container",
        id="network-container",
        children=[network_panel(), network_graph_panel()],
    )

def network_panel():
    return html.Div(
        className="network-container__upload__wrapper",
        id="network-container__upload__wrapper",
    )

def network_graph_panel():
    return html.Div(
        className="network_graph-container__upload__wrapper",
        id="network_graph-wrapper",
    )
