#!/usr/bin/env python3

from courselib.instructor_access import InstructorAccess
from config import config
import os

output = config["wsl_mapper"]["output_file"]
output_dir = os.path.dirname(output)

col1_w = 45
col2_w = 38
col3_w = 47


def output_rst(lab, lab_tas, students, output):
    names = [val['name'] for val in students.values()]
    names.sort()
    divider = len(lab_tas)
    chunk = len(names)//divider
    idx1 = 1
    idx2 = 1
    pos = 0

    if chunk == 0:
        chunk = 1

    for i, ta in enumerate(lab_tas):
        joined = " ".join([lab['days'], lab['time'],
                           lab['bldg'], lab['room'],
                           "(" + str(lab['crn']) + ")"])
        print("{s:{col1}s}".format(s=joined, col1=col1_w+1), end="",
              file=output)

        s1 = names[pos:pos+chunk][0]   # First name in section
        s2 = names[pos:pos+chunk][-1]  # Last name in section

        try:
            s3 = names[pos+chunk]  # Name starting next range
            idx2 = [i for i in range(len(s3 if s2 > s3 else s2)) if s2[i] !=
                    s3[i]][0] + 1
        except IndexError:
            pass

        stud_list_name = output_dir + "/lab-{}-{}.rst".format(lab['crn'],
                                                              divider)
        with open(stud_list_name, 'w') as student_list_file:
            title_str = "Student List for {}, part {}".format(lab['crn'],
                                                              divider)
            print(":orphan:\n", file=student_list_file)
            print(title_str, file=student_list_file)
            print("#"*len(title_str), file=student_list_file)
            for name in names[pos:pos+chunk]:
                print("   #. {}".format(name), file=student_list_file)

        sect_range = ":doc:`{0} - {1} <lab-{3}-{4}>` — [{5}]"\
            .format(s1[0:idx1],
                    s2[0:idx2],
                    len(names[pos:
                              pos +
                              chunk]),
                    lab['crn'],
                    divider,
                    len(names[pos:pos+chunk]))

        print("{s:{col2}s}".format(s=sect_range, col2=col2_w+1), end="",
              file=output)

        joined = " ".join([ta['name'], ta['email']])
        print("{s:{col3}s}".format(s=joined, col3=col3_w+1),
              file=output)

        if i == (len(lab_tas) - 1):
            print("{} {} {}".format("-"*col1_w, "-"*col2_w, "-"*col3_w),
                  file=output)

        pos += chunk
        rem = len(names) - pos
        if rem - pos < chunk:
            chunk += rem
        divider -= 1
        idx1 = idx2
        idx2 = 1


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

    with open(config["ta_mapper"]["output_file"], 'w') as output:
        table_str = "="*col1_w + " " + "="*col2_w + " " + "="*col3_w + "\n"
        output.write(table_str)

        print("{s:{col1}s}".format(s="If your registered lab session is…",
                                   col1=col1_w),
              "{s:{col2}s}".format(s="and your last name starts with…",
                                   col2=col2_w),
              "{s:{col3}s}".format(s="then, your lab TA is:",
                                   col3=col3_w), file=output)
        output.write(table_str)

        students_lists_lecture = access.roster_query(term, lecture_crn)
        students_lecture = {}

        for lab_crn in config['registrar']['labs']:
            if not lab_crn:
                continue

            if lab_crn not in courses:
                print("Lab session CRN {0} not found. Skipping…"
                      .format(lab_crn))
                continue

            tas = config['admin']['lab_TAs'][lab_crn]

            students_lab = access.roster_query(term, lab_crn)[lab_crn]
            lab_keys = set(students_lab.keys())
            for key in (lab_keys - lecture_keys):
                print("Student {0} is in lab {1} but not in lecture section."
                      .format(students_lab[key]['name'], lab_crn))
                del students_lab[key]

            output_rst(courses[lab_crn], tas, students_lab, output)

        # Little hackey hack to remove the last '---' border from the TA
        # listing above.
        output.seek(output.tell()-len(table_str))
        output.write(table_str)

    access.logout()

main()
