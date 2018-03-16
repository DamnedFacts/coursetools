from yaml import load, dump

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

with open('config/config.yaml') as f:
    config = load(f, Loader=Loader)

with open(config['gen_sched']['yaml_output_file']) as f:
    duedates = load(f, Loader=Loader)
    config['admin']['due_dates'] = duedates

with open("config/lab_tas.yaml") as f:
    lab_tas = load(f, Loader=Loader)
    config['admin']['lab_TAs'] = lab_tas

with open("config/workshop_leaders.yaml") as f:
    workshop_leaders = load(f, Loader=Loader)
    config['admin']['workshop_leaders'] = workshop_leaders
