#!/usr/bin/env python3

from courselib.blackboard import BlackBoard
import sys
from pprint import pprint

bb = BlackBoard()
bb.login()

try:
    parent = sys.argv[1]
    items = bb.list_content(parent)
    pprint(items)
except IndexError:
    print("Please supply a parent ID.")
