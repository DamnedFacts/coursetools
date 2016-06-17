#!/usr/bin/env python3

from courselib.blackboard import BlackBoard
from config import config

bb = BlackBoard()
bb.login()

wsl = config['admin']['workshop_leaders'].values()
tas = config['admin']['lab_TAs'].values()
helpers = list(wsl) + [l for sublist in tas for l in sublist]

for helper in helpers:
    bb.add_user(helper['netid'], "T")

bb.logout()
