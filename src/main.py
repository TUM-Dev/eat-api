# -*- coding: utf-8 -*-
import json
import os
import sys
from typing import Dict, Optional

import cli
import enum_json_creator
import menu_parser
from entities import Canteen, Week
from openmensa import openmensa
from utils import util

JSON_VERSION: str = "2.1"
"""
The current version of the JSON output.
Should be incremented as soon as the JSON output format changed in any way, shape or form.
"""


def get_menu_parsing_strategy(canteen: Canteen) -> Optional[menu_parser.MenuParser]:
    parsers = {
        menu_parser.StudentenwerkMenuParser,
        menu_parser.FMIBistroMenuParser,
        menu_parser.MedizinerMensaMenuParser,
        menu_parser.StraubingMensaMenuParser,
        menu_parser.MensaBildungscampusHeilbronnParser,
    }
    # set parsing strategy based on canteen
    for parser in parsers:
        if canteen in parser.canteens:
            return parser()
    return None


def jsonify(weeks: Dict[int, Week], directory: str, canteen: Canteen, combine_dishes: bool) -> None:
    # iterate through weeks
    for calendar_week, week in weeks.items():
        # get year of calendar week
        year = week.year

        # create dir: <year>/
        json_dir = f"{directory}/{year}"
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)

        # convert Week object to JSON
        week_json = week.to_json_obj()
        if week_json is not None:
            week_json["version"] = JSON_VERSION
        # write JSON to file: <year>/<calendar_week>.json
        with open(f"{json_dir}/{calendar_week:02}.json", "w", encoding="utf-8") as outfile:  # noqa: E231
            json.dump(week_json, outfile, separators=(",", ":"), ensure_ascii=False)

    # check if combine parameter got set
    if not combine_dishes:
        return
    # the name of the output directory and file
    combined_df_name = "combined"

    # create directory for combined output
    json_dir = f"{directory}/{combined_df_name}"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    # convert all weeks to one JSON object
    weeks_json_all = json.dumps(
        {
            "version": JSON_VERSION,
            "canteen_id": canteen.canteen_id,
            "weeks": [weeks[calendar_week].to_json_obj() for calendar_week in weeks],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )

    # write JSON object to file
    with open(f"{json_dir}/{combined_df_name}.json", "w", encoding="utf-8") as outfile:
        json.dump(json.loads(weeks_json_all), outfile, separators=(",", ":"), ensure_ascii=False)


def main():
    # get command line args
    args = cli.parse_cli_args()

    if args.print_canteens:
        sys.exit(enum_json_creator.enum_to_api_representation_dict(list(Canteen)))
    if args.canteen_ids:
        for c in list(Canteen):
            print(c.canteen_id)
        sys.exit()

    canteen = Canteen.get_canteen_by_str(args.canteen)
    # get required parser
    parser = get_menu_parsing_strategy(canteen)
    if not parser:
        sys.exit("Canteen parser not found")

    menus = parser.parse(canteen)
    if menus is None:
        sys.exit("Error. Could not retrieve menu(s)")

    # optionally translate the dish titles
    if args.language is not None and args.language.upper() != "DE":
        util.translate_dishes(menus, args.language)

    # if date has been explicitly specified, try to parse it
    menu_date = None
    if args.date is not None:
        try:
            menu_date = util.parse_date(args.date)
        except ValueError:
            print(f"Error during parsing date from command line: {args.date}")
            sys.exit(f"Required format: {util.cli_date_format}")

    # jsonify argument is set
    if args.jsonify is not None:
        weeks = Week.to_weeks(menus)
        if not os.path.exists(args.jsonify):
            os.makedirs(args.jsonify)
        jsonify(weeks, args.jsonify, canteen, args.combine)
    elif args.openmensa is not None:
        weeks = Week.to_weeks(menus)
        if not os.path.exists(args.openmensa):
            os.makedirs(args.openmensa)
        openmensa(weeks, args.openmensa)
    # date argument is set
    elif args.date is not None:
        if menu_date not in menus:
            sys.exit(f"There is no menu for '{canteen}' on {menu_date}!")
        menu = menus[menu_date]
        print(menu)
    # print weeks otherwise
    elif menus is not None:
        weeks = Week.to_weeks(menus)
        for calendar_week in weeks:
            print(weeks[calendar_week])


if __name__ == "__main__":
    main()
