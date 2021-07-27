import json
import logging

from battery_class_new import battery_class_new
from sim_runner_no_dashboard import construct_use_case_library

_log = logging.getLogger(__name__)


def __init_gen_config__():
    _log.debug("Loading gen_config")
    with open("dict.json", 'r', encoding='utf-8') as lp:
        gconfig = json.load(lp)
    return gconfig


def __init_control_config__():
    _log.debug("Loading control_config")
    with open("control_fields.json", 'r', encoding='utf-8') as lp:
        cconfig = json.load(lp)
    return cconfig


def __init_data_config__():
    _log.debug("Loading data_config")
    with open("data_paths.json", 'r', encoding='utf-8') as lp:
        dconfig = json.load(lp)
    return dconfig


data_config = __init_data_config__()
gen_config = __init_gen_config__()
control_config = __init_control_config__()
_log.debug("Constructing use case library")
# Instead of using two loads for this just construct it here.
use_case_library = construct_use_case_library(gen_config, control_config)
battery_obj = battery_class_new(use_case_library, gen_config, data_config)
# Initial loading of battery data into the simulation.  Probably should be
# called load data but leaving it alone for now.
battery_obj.get_data()
