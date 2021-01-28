# -*- coding: utf-8 -*-

import argparse

from menu_parser import StudentenwerkMenuParser


def parse_cli_args():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    group: argparse._MutuallyExclusiveGroup = parser.add_mutually_exclusive_group(  # pylint: disable=protected-access
        required=True,
    )
    group.add_argument(
        "-p",
        "--parse",
        metavar="LOCATION",
        dest="location",
        choices=(
            ["fmi-bistro", "ipp-bistro", "mediziner-mensa"]
            + list(StudentenwerkMenuParser.location_id_mapping.keys())
        ),
        help="the location you want to eat at",
    )
    parseGroup: argparse._MutuallyExclusiveGroup = group.add_argument_group("parse")  # pylint: disable=protected-access
    parseGroup.add_argument("-d", "--date", help="date (DD.MM.YYYY) of the day of which you want to get the menu")
    parseGroup.add_argument(
        "-j",
        "--jsonify",
        help="directory for JSON output (date parameter will be ignored if this argument is used)",
        metavar="PATH",
    )
    parseGroup.add_argument(
        "-c",
        "--combine",
        action="store_true",
        help='creates a "combined.json" file containing all dishes for the location specified',
    )
    parseGroup.add_argument(
        "--openmensa",
        help="directory for OpenMensa XML output (date parameter will be ignored if this argument is used)",
        metavar="PATH",
    )
    group.add_argument(
        "-l",
        "--locations",
        action="store_true",
        help="prints all available locations formated as JSON",
    )
    return parser.parse_args()
