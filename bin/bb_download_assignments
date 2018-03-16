#!/usr/bin/env python3

import courselib.blackboard


def main():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('assignment', metavar='<name or column id>', type=str,
                        help='The  name, or BB column id for the assignment')

    args = parser.parse_args()

    # Log into Blackboard
    b = courselib.blackboard.BlackBoard()
    b.login()

    b.download_assignment(args.assignment, all_select=True)

    # Logout of Blackboard
    b.logout()

if __name__ == '__main__':
    main()
