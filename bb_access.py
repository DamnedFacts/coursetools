#!/usr/bin/env python3

from courselib.instructor_access import InstructorAccess

access = InstructorAccess()

access.login()


def add_bb_user(course, user_id, role):
    pass


def print_bb_users(course, user_id=None):
    pass


def main():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--course",
                        type=str,
                        nargs="?",
                        default=None,
                        help="select a BlackBoard course ID",
                        required=True,
                        action='store')

    parser.add_argument("-i", "--id",
                        type=str,
                        nargs="?",
                        default=None,
                        help="select a BlackBoard User ID",
                        required=False,
                        action='store')

    parser.add_argument("-a", "--add",
                        type=str,
                        nargs="?",
                        default=None,
                        help="add the given BB ID to the the course, with \
                        role '<role>'",
                        required=False,
                        action='store')

    parser.add_argument("-j", "--json",
                        help="Prints output as JSON",
                        required=False,
                        action='store_true')

    args = parser.parse_args()

    if not args.quiet:
        print(args)

    # Log into Blackboard
    access.login()

    if args.course and args.id:
        print_bb_users(args.course, user_id=args.id)
    elif args.course and args.id and args.add:
        add_bb_user(args.course, args.id, args.add)
    else:
        print_bb_users(args.course)

    # Logout of Blackboard
    access.logout()

if __name__ == '__main__':
    main()
