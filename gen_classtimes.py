#!/usr/bin/env python3

from courselib.instructor_access import InstructorAccess
from config import config
import argparse
import sys
from collections import OrderedDict


def plain_out(courses, output_file):
    for crn in config['registrar']['crn']:
        if crn not in courses:
            print("Uknown CRN: {0}".format(crn))
            continue

        print("Section {0}: {1} {2} {3} {4}"
              .format(crn,
                      courses[crn]['days'],
                      courses[crn]['time'],
                      courses[crn]['bldg'],
                      courses[crn]['room']), file=output_file)


def rst_table_borders(cols):
    s = ""
    for k, v in cols.items():
        s += "=" * v + " "

    return s[:-1]


def rst_out(courses, output_file):
    cat = ['section', 'days', 'time', 'bldg', 'room']
    maxes = [0] * len(cat)

    for crn in config['registrar']['crn']:
        courses[crn]['section'] = str(crn)
        for i in range(len(cat)):
            maxes[i] = max(len(cat[i]), len(courses[crn][cat[i]]), maxes[i])

    lens = OrderedDict(zip(cat, maxes))

    print(rst_table_borders(lens), file=output_file)

    for k, v in lens.items():
        print("{0:{1}}".format(k.capitalize(), v+1), end="", file=output_file)

    print("\n" + rst_table_borders(lens), file=output_file)

    for crn in config['registrar']['crn']:
        for i in range(len(cat)):
            print("{0:{1}}".format(courses[crn][cat[i]], maxes[i] + 1),
                  end="",
                  file=output_file)
        print(file=output_file)

    print(rst_table_borders(lens), file=output_file)


def main():
    access = InstructorAccess()
    access.login()
    courses = access.course_query(config['registrar']['term'])
    access.logout()

    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--rst-output",
                        help="Prints output as ReStructuredText table",
                        required=False,
                        action='store_true')
    parser.add_argument("-w", "--write",
                        help="Write output to file specified in config.yaml",
                        required=False,
                        action='store_true')

    args = parser.parse_args()

    if args.write:
        filename = config['gen_classtimes']['output_file']
        output_file = open(filename, 'w')
    else:
        output_file = sys.stdout

    if args.rst_output:
        rst_out(courses, output_file)
    else:
        plain_out(courses, output_file)

    output_file.close()

if __name__ == "__main__":
    main()
