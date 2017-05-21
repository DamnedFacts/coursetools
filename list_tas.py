#!/usr/bin/env python3

from courselib.instructor_access import InstructorAccess
from config import config

access = InstructorAccess()
access.login()
term = config['registrar']['term']
courses = access.course_query(term)

for lab_crn in config['registrar']['labs']:
    if lab_crn not in courses:
        continue

    lab = config['admin']['lab_TAs'][lab_crn]
    for ta in lab:
        person = "{0} <{1}>".format(ta['name'], ta['email'])

        print("{0:50} {1} {2} {3} {4}\t[{5}]".format(person,
                                                     courses[lab_crn]['days'],
                                                     courses[lab_crn]['time'],
                                                     courses[lab_crn]['bldg'],
                                                     courses[lab_crn]['room'],
                                                     lab_crn))
access.logout()
