#!/usr/bin/env python3

from courselib.instructor_access import InstructorAccess
from config import config

access = InstructorAccess()
access.login()
term = config['registrar']['term']
courses = access.course_query(term)

for ws_crn in config['registrar']['workshops']:
    if ws_crn not in courses:
        continue

    ws = config['admin']['workshop_leaders'][ws_crn]
    person = "{0} <{1}>".format(ws['name'], ws['email'])

    print("{0:60} {7:10} {1:4} {2:10} {3:10} {4:10} [{5}] [{6} students]"
          .format(person,
                  courses[ws_crn]['days'],
                  courses[ws_crn]['time'],
                  courses[ws_crn]['bldg'],
                  courses[ws_crn]['room'],
                  ws_crn,
                  courses[ws_crn]['enrolled'],
                  ws['netid']))

access.logout()
