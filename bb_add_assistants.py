#!/usr/bin/env python3

from courselib.blackboard import BlackBoard
from config import config

bb = BlackBoard()
bb.login()

print("Adding workshop leaders and lab TAs to course id {0}"
      .format(config['registrar']['blackboard']['course_id']))
wsl = config['admin']['workshop_leaders'].values()
tas = config['admin']['lab_TAs'].values()
gta = config['admin']['grad_TAs']

helpers = [w for w in wsl if w['netid']] + \
    [t for sublist in tas for t in sublist if t['netid']] + \
    [g for g in gta if g['netid']]

for helper in helpers:
    bb.add_user(helper['netid'], "T")

bb.logout()
