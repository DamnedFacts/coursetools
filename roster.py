#!/usr/bin/env python3

from courselib.instructor_access import InstructorAccess


access = InstructorAccess()


def print_terms(args):
    # Get list of available terms
    terms = access.term_query()
    for t in terms:
        t = t.replace(" ", "_")
        print("    {0}".format(t))


def print_permission_code(args):
    # Get list of available course for that term
    term = args.term
    access.term_query()
    permission_code = access.permission_code_query(term)
    print("The permission code for {0}: {1}".format(term, permission_code))


def print_courses(args):
    # Get list of available course for that term
    term = args.term
    access.term_query()
    courses = access.course_query(term)

    courses = courses.values()

    print("{0:8s}{1:10s}{2:33s}{3:7s}{4:12s}{5:7s}{6:7s}{7:13s}{8:8s}"
          .format(
              "CRN", "Course", "Course Title", "Days",
              "Time", "Bldg", "Room", "Sect Enrol", "Sect Cap"))

    for v in courses:
        print("{0:<8d}{1:10s}{2:33s}{3:7s}{4:12s}{5:7s}{6:7s}{7:<13d}{8:<8d}"
              .format(
                  v["crn"], v["course"], v["course_title"], v["days"],
                  v["time"], v["bldg"], v["room"], v["enrolled"],
                  v["cap"]))

        childs = v.get('crn_child')
        if childs:
            for c in childs:
                print("{0:<8d}{1:76s}{2:<13d}{3:<8d}"
                      .format(childs[c]["crn"], childs[c]["course"],
                              childs[c]["enrolled"], childs[c]["cap"]))
            else:
                print("{0:>84s}{1:<13d}{2:<8d}"
                      .format("Total: ", v['cls_enrol'], v['cls_cap']))


def print_roster_json(args):
    import json

    term = args.term
    crn = args.course

    access.term_query()
    access.course_query(term)

    students = access.roster_query(term, crn)

    print(json.dumps(students))


def print_roster(args):
    term = args.term
    crn = int(args.course)

    # Get Roster
    access.term_query()
    courses = access.course_query(term)
    if crn not in courses:
        for course in courses:
            if 'crn_child' in course and course['crn_child'] == crn:
                print(course)

    student_rosters = access.roster_query(term, crn)

    for course_crn, students in student_rosters.items():
        
        if not args.quiet:
            try:

                print("\nRoster for {0} ({1}, {2})"
                      .format(courses[crn]['course_title'],
                              courses[course_crn]['course'], course_crn))
            except KeyError:
                print("\nRoster for {0} ({1}, {2})"
                      .format(courses[crn]['course_title'],
                              courses[crn]['crn_child'][course_crn]['course'],
                              course_crn))

        values = sorted(list(students.values()),
                        key=lambda student: student['name'])

        for v in values:
            name = v['name']
            email = v['email']
            stud_id = v['stud_id']
            college = v['college']
            class_year = v['class_year']
            major = v['major']
            deg = v['deg']
            hrs = v['hrs']
            grade = v['grade']
            status = v['status']
            update = v['update']

            print("{:<25} <{:<20}>\t{:<10}\t{:<10}\t{:<10}\t"
                  "{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\t"
                  "{:<10}".format(name, email, stud_id, college,
                                  class_year, major, deg, hrs, grade,
                                  status, update))


def print_roster_mail(args):
    term = args.term
    crn = int(args.course)

    # Get Roster
    access.term_query()
    courses = access.course_query(term)
    if crn not in courses:
        for course in courses:
            if 'crn_child' in course and course['crn_child'] == crn:
                print(course)

    student_rosters = access.roster_query(term, crn)

    for course_crn, students in student_rosters.items():
        
        if not args.quiet:
            try:

                print("\nRoster for {0} ({1}, {2})"
                      .format(courses[crn]['course_title'],
                              courses[course_crn]['course'], course_crn))
            except KeyError:
                print("\nRoster for {0} ({1}, {2})"
                      .format(courses[crn]['course_title'],
                              courses[crn]['crn_child'][course_crn]['course'],
                              course_crn))

        values = sorted(list(students.values()),
                        key=lambda student: student['name'])

        for v in values:
            first, last = v['name'].split(",")
            email = v['email']

            print("{0} {1} <{2}>".format(first.strip(), last.strip(), email))


def main():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--term",
                        type=str,
                        nargs="?",
                        default=None,
                        help="select a term to view",
                        required=False,
                        action='store')

    parser.add_argument("-c", "--course",
                        type=str,
                        nargs="?",
                        default=None,
                        help="select course to view of the given term",
                        required=False,
                        action='store')

    parser.add_argument("-m", "--mail",
                        help="display only the names and e-mails"
                        "of students in course",
                        required=False,
                        action='store_true')

    parser.add_argument("-q", "--quiet",
                        help="Prints output without headers \
                              and other info",
                        required=False,
                        action='store_true')

    parser.add_argument("-j", "--json",
                        help="Prints output as JSON",
                        required=False,
                        action='store_true')

    parser.add_argument("-P", "--permission-code",
                        required=False,
                        action="store_true")

    args = parser.parse_args()

    if not args.quiet:
        print(args)

    # Log into Blackboard
    access.login()

    if args.permission_code and args.term:
        print_permission_code(args)
    elif not (args.term or args.course):
        print("\nAvailable terms to select from:")
        print_terms(args)
    elif args.term and not args.course:
        print("\nAvailable courses to choose from for " + args.term)
        print_courses(args)
    else:
        if args.json:
            print_roster_json(args)
        elif args.mail:
            print_roster_mail(args)
        else:
            print_roster(args)

    # Logout of Blackboard
    access.logout()

if __name__ == '__main__':
    main()
