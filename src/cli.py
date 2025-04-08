# -*- coding: utf-8 -*-

import argparse

from entities import Canteen


def parse_cli_args():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    action_group: argparse._MutuallyExclusiveGroup = parser.add_mutually_exclusive_group(
        required=True,
    )
    action_group.add_argument(
        "-p",
        "--parse",
        metavar="CANTEEN",
        dest="canteen",
        choices=(Canteen._member_names_ + [key.canteen_id for key in Canteen]),
        help="the canteen you want to eat at",
    )
    action_group.add_argument(
        "--canteen-ids",
        action="store_true",
        help="prints all available canteen IDs to stdout with a new line after each canteen",
    )
    action_group.add_argument(
        "--print-canteens",
        action="store_true",
        help="prints all available canteens formated as JSON",
    )

    parser.add_argument(
        "--language",
        help="The language to translate the dish titles to, "
        "needs an DeepL API-Key in the environment variable DEEPL_API_KEY_EAT_API",
    )

    output_group: argparse._MutuallyExclusiveGroup = (
        parser.add_mutually_exclusive_group()
    )
    output_group.add_argument(
        "-j",
        "--jsonify",
        help="directory for JSON output",
        metavar="PATH",
    )
    output_group.add_argument(
        "--openmensa",
        help="directory for OpenMensa XML output",
        metavar="PATH",
    )
    output_group.add_argument("-d", "--date", help="date (DD.MM.YYYY) of the day of which you want to get the menu")

    parser.add_argument(
        "-c",
        "--combine",
        action="store_true",
        help='only for jsonify: creates a "combined.json" file containing all dishes for the canteen specified',
    )
    return parser.parse_args()
