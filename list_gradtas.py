#!/usr/bin/env python3

from config import config
from collections import OrderedDict
import sys


def plain_out(output_file):
    for gta in config['admin']['grad_TAs']:
        person = "{0} <{1}>".format(gta['name'], gta['email'])
        print("{0:50} {1} {2}".format(person,
                                      gta['office'],
                                      gta['hours']), file=output_file)


def rst_table_borders(cols):
    s = ""
    for k, v in cols.items():
        s += "=" * v + " "

    return s[:-1]


def rst_out(output_file):
    gtas = config['admin']['grad_TAs']
    cat = ['name', 'email', 'office', 'hours']
    maxes = [0] * len(cat)

    for gta in gtas:
        for i in range(len(cat)):
            maxes[i] = max(len(cat[i]), len(gta[cat[i]]), maxes[i])

    lens = OrderedDict(zip(cat, maxes))

    print(rst_table_borders(lens), file=output_file)

    for k, v in lens.items():
        print("{0:{1}}".format(k.capitalize(), v+1), end="", file=output_file)

    print("\n" + rst_table_borders(lens), file=output_file)

    for gta in config['admin']['grad_TAs']:
        for i in range(len(cat)):
            print("{0:{1}}".format(gta[cat[i]], maxes[i] + 1),
                  end="",
                  file=output_file)
        print(file=output_file)

    print(rst_table_borders(lens), file=output_file)


def main():
    import argparse
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
        filename = config['list_gradtas']['output_file']
        output_file = open(filename, 'w')
    else:
        output_file = sys.stdout

    if args.rst_output:
        rst_out(output_file)
    else:
        plain_out(output_file)

    output_file.close()

if __name__ == "__main__":
    main()
