from typing import Optional
import dash_core_components as dcc
import dash_html_components as html


def common_dropdown_box(id: str, default_value: str):
    """
    id: the html element that is created such that you can style/use javascript to manipulate
        (MUST BE UNIQUE ACROSS ALL ELEMENTS ON THE PAGE)
    default_value: the default value of the form submittion element one of .
    """
    options = ["GI", "PL", "GR", "BR", "PF", "EP", "D"]
    if default_value not in options:
        raise ValueError(f'Invalid option specified must be one of ({",".join(options)})')
    return dcc.Dropdown(
        id=id,  # 'fig-left-dropdown',
        options=[
            {'label': 'Grid Import', 'value': 'GI'},
            {'label': 'Peak Load', 'value': 'PL'},
            {'label': 'Grid Reactive', 'value': 'GR'},
            {'label': 'Battery Reactive', 'value': 'BR'},
            {'label': 'Power Factor', 'value': 'PF'},
            {'label': 'Energy Price', 'value': 'EP'},
            {'label': 'Demand', 'value': 'D'}
        ],
        # placeholder="Left y-axis (default = Grid Import)",
        value=default_value  # 'GI'
    )


def common_graph(id: str, dropdown_default: Optional[str] = None):
    """
    Create a graph component with optional dropdown using the common_dropdown_box function.
    
    The common_dropdown_box will be added if the dropdown_default is set to something
    other than None.

    The name of the id for the dropdown will be concatinated from the id passed and
    then appended with -dropdown.  

    Example of dropdown_id is:
        id = "myfigure"
        dropdown_box will be myfigure-dropdown
    """
    children = [dcc.Graph(id=id, animate=True)]

    if dropdown_default:
        children.insert(0, common_dropdown_box(id=f"{id}-dropdown", default_value=dropdown_default))
    return html.Div(children)


def common_slider(id: str, className: str, label_name, label_style,
                  default_value=0, min=-100, max=100, step=20, updatemode='drag'):
    """
    Create a slide component
    """
    marks = {-100: '-100 %',
             -75: '-75 %',
             -50: '-50 %',
             -25: '-25 %',
             0: '0 %',
             25: '25 %',
             50: '50 %',
             75: '75 %',
             100: '100 %'
             }
    return html.Div([
        html.Label(label_name, style=label_style),
        dcc.Slider(
            id=id,
            className=className,
            min=min,
            max=max,
            step=step,
            marks=marks,
            value=default_value,
            updatemode=updatemode
        ),
    ])
