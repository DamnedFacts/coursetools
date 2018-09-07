import os
from yaml import load, dump

basedir = os.environ['COURSETOOLS_BASE']

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

with open(basedir + 'config/config.yaml') as f:
    config = load(f, Loader=Loader)

with open(basedir + config['gen_sched']['yaml_output_file']) as f:
    duedates = load(f, Loader=Loader)
    config['admin']['due_dates'] = duedates

with open(basedir + "config/lab_tas.yaml") as f:
    lab_tas = load(f, Loader=Loader)
    config['admin']['lab_TAs'] = {tas: lab_tas[tas] for tas in lab_tas
                                  if lab_tas[tas]}
    config['registrar']['labs'] = [crn for crn in config['admin']['lab_TAs']
                                   if crn not in config['registrar']['crn']]

with open(basedir + "config/workshop_leaders.yaml") as f:
    workshop_leaders = load(f, Loader=Loader)
    config['admin']['workshop_leaders'] = workshop_leaders
    config['registrar']['workshops'] = list(config['admin']['workshop_leaders'].keys())
