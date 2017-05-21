#!/usr/bin/env python3

from courselib.instructor_access import InstructorAccess
from config import config
import os

output = config["wsl_mapper"]["output_file"]
output_dir = os.path.dirname(output)

col1_w = 38
col2_w = 38
col3_w = 47


def output_rst(courses, crn, leader, students, output, config):
    ws = courses[crn]
    names = [val['name'] for val in students.values()]
    names.sort()

    joined = " ".join([ws['days'], ws['time'], ws['bldg'],
                       ws['room'], "(" + str(crn) + ")"])
    print("{s:{col1}s}".format(s=joined, col1=col1_w+1), end="",
          file=output)

    stud_list_name = output_dir + "/ws-{}.rst".format(ws['crn'])
    with open(stud_list_name, 'w') as student_list_file:
        title_str = "Student List" " \
            for *{0}* ({1})".format(ws['course_title'].title(),
                                    ws['crn'])
        print(":orphan:\n", file=student_list_file)
        print(title_str, file=student_list_file)
        print("#"*len(title_str), file=student_list_file)
        for name in names:
            print("   #. {}".format(name), file=student_list_file)

    sect_range = ":doc:`Student List <ws-{0}>` — [{1}]"\
        .format(ws['crn'], len(names))

    print("{s:{col2}s}".format(s=sect_range, col2=col2_w+1), end="",
          file=output)

    joined = " ".join([leader['name'], leader['email']])
    print("{s:{col3}s}".format(s=joined, col3=col3_w+1),
          file=output)

    if crn != config['registrar']['workshops'][-1]:
        print("{} {} {}".format("-"*col1_w, "-"*col2_w, "-"*col3_w),
              file=output)


def main():
    term = config['registrar']['term']

    access = InstructorAccess()
    access.login()
    courses = access.course_query(term)

    # Retrieve full student list for lecture(s) CRN.
    students_lecture = {}
    for lecture_crn in config['registrar']['crn']:
        students_dict = access.roster_query(term, lecture_crn)[lecture_crn]
        students_lecture = {**students_lecture, **students_dict}
    lecture_keys = set(students_lecture.keys())

    with open(config["wsl_mapper"]["output_file"], 'w') as output:
        print("{} {} {}".format("="*col1_w, "="*col2_w, "="*col3_w),
              file=output)
        print("{s:{col1}s}".format(s="If your registered workshop is…",
                                   col1=col1_w),
              "{s:{col2}s}".format(s="the student list is…",
                                   col2=col2_w),
              "{s:{col3}s}".format(s="and, your workshop leader is:",
                                   col3=col3_w), file=output)
        print("{} {} {}".format("="*col1_w, "="*col2_w, "="*col3_w),
              file=output)

        for ws_crn in config['registrar']['workshops']:
            if not ws_crn:
                continue

            if ws_crn not in courses:
                print("Workshop CRN {0} not found. Skipping…".format(ws_crn))
                continue

            wsl = config['admin']['workshop_leaders'][ws_crn]

            students_ws = access.roster_query(term, ws_crn)[ws_crn]
            ws_keys = set(students_ws.keys())
            for key in (ws_keys - lecture_keys):
                print("Student {0} is in ws {1} but not in lecture section."
                      .format(students_ws[key]['name'], ws_crn))
                del students_ws[key]

            output_rst(courses, ws_crn, wsl, students_ws, output, config)

        print("{} {} {}".format("="*col1_w, "="*col2_w, "="*col3_w),
              file=output)
        access.logout()

main()
