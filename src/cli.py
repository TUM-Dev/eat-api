# -*- coding: utf-8 -*-

import argparse

from entities import Canteen


def parse_cli_args():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    group: argparse._MutuallyExclusiveGroup = parser.add_mutually_exclusive_group(  # pylint: disable=protected-access
        required=True,
    )
    group.add_argument(
        "-p",
        "--parse",
        metavar="CANTEEN",
        dest="canteen",
        # pylint:disable=protected-access
        choices=(Canteen._member_names_ + [key.canteen_id for key in Canteen]),
        # pylint:enable=protected-access
        help="the canteen you want to eat at",
    )
    parseGroup: argparse._MutuallyExclusiveGroup = group.add_argument_group(
        "parse",
    )  # type: ignore # pylint: disable=protected-access
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
        help='creates a "combined.json" file containing all dishes for the canteen specified',
    )
    parseGroup.add_argument(
        "--openmensa",
        help="directory for OpenMensa XML output (date parameter will be ignored if this argument is used)",
        metavar="PATH",
    )
    group.add_argument(
        "--canteens",
        action="store_true",
        help="prints all available canteens formated as JSON",
    )
    parser.add_argument(
        "--language",
        help="The language to translate the dish titles to, "
        "needs an DeepL API-Key in the environment variable DEEPL_API_KEY_EAT_API",
    )
    return parser.parse_args()
