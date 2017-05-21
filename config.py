from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

with open('config.yaml') as f:
    config = load(f, Loader=Loader)

with open(config['gen_sched']['yaml_output_file']) as f:
    duedates = load(f, Loader=Loader)
    config['admin']['due_dates'] = duedates
