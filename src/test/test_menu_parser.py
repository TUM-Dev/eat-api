# -*- coding: utf-8 -*-
import datetime
import os
import tempfile
from datetime import date
from typing import Dict

import pytest
from lxml import html  # nosec: https://github.com/TUM-Dev/eat-api/issues/19
from syrupy.extensions.json import JSONSnapshotExtension

from src import main
from src.entities import Canteen, Menu, Week
from src.menu_parser import (
    FMIBistroMenuParser,
    MedizinerMensaMenuParser,
    MenuParser,
    StraubingMensaMenuParser,
    StudentenwerkMenuParser,
)
from src.utils import file_util, json_util


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.with_defaults(extension_class=JSONSnapshotExtension)


def test_get_date():
    assert MenuParser.get_date(2017, 44, 1) == date(2017, 10, 30)
    assert MenuParser.get_date(2018, 1, 1) == date(2018, 1, 1)
    assert MenuParser.get_date(2019, 2, 1) == date(2019, 1, 7)


class TestStudentenwerkMenuParser:
    studentenwerk_menu_parser = StudentenwerkMenuParser()

    base_path_canteen = "src/test/assets/studentenwerk/{canteen}"

    test_dates = [
        date(2024, 7, 29),
        date(2024, 7, 30),
        date(2024, 7, 31),
        date(2024, 8, 1),
        date(2024, 8, 2),
        date(2024, 8, 5),
        date(2024, 8, 6),
        date(2024, 8, 7),
        date(2024, 8, 8),
        date(2024, 8, 9),
    ]

    def test_get_all_dates(self) -> None:
        working_days = []

        start_date = date(2024, 7, 23)
        end_date = date(2024, 8, 30)
        holidays = {date(2024, 8, 15)}

        while start_date <= end_date:
            # 5 is Saturday, 6 is Sunday
            if start_date.weekday() not in {5, 6} and start_date not in holidays:
                working_days.append(start_date)
            start_date += datetime.timedelta(days=1)

        dates = []
        tree = file_util.load_html(
            f"{self.base_path_canteen.format(canteen=Canteen.MENSA_GARCHING.canteen_id)}/for-generation/overview.html",
        )
        menus = StudentenwerkMenuParser.get_daily_menus_as_html(tree)
        for menu in menus:
            html_menu = html.fromstring(html.tostring(menu))
            dates.append(self.studentenwerk_menu_parser.extract_date_from_html(html_menu))
        assert dates == working_days

    def test_studentenwerk(self, snapshot_json):
        canteens = [Canteen.MENSA_ARCISSTR, Canteen.STUBISTRO_BUTENANDSTR, Canteen.MENSA_GARCHING]
        for canteen in canteens:
            self.__test_studentenwerk_canteen(canteen, snapshot_json)

    def __test_studentenwerk_canteen(self, canteen, snapshot_json):
        menus = self.__get_menus(canteen)
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, canteen, True)
            assert file_util.load_ordered_json(os.path.join(temp_dir, "combined", "combined.json")) == snapshot_json

    def __get_menus(self, canteen: Canteen) -> Dict[date, Menu]:
        menus = {}
        for date_ in self.test_dates:
            # parse the menu
            tree: html.Element = file_util.load_html(
                f"{self.base_path_canteen.format(canteen=canteen.canteen_id)}/for-generation/{date_}.html",
            )
            studentenwerk_menu_parser = StudentenwerkMenuParser()
            menu = studentenwerk_menu_parser.get_menu(tree, canteen)
            if menu is not None:
                menus[date_] = menu
        return menus

    def test_should_return_weeks_when_converting_menu_to_week_objects(self):
        menus = self.__get_menus(Canteen.MENSA_GARCHING)
        weeks_actual = Week.to_weeks(menus)
        length_weeks_actual = len(weeks_actual)

        assert length_weeks_actual == 2
        for calendar_week in weeks_actual:
            week = weeks_actual[calendar_week]
            week_length = len(week.days)
            assert week_length == 5

    def test_should_convert_week_to_json(self, snapshot_json):
        calendar_weeks = [31, 32]
        menus = self.__get_menus(Canteen.MENSA_GARCHING)
        weeks = Week.to_weeks(menus)
        for calendar_week in calendar_weeks:
            generated_week = json_util.order_json_objects(weeks[calendar_week].to_json_obj())
            assert generated_week == snapshot_json


class TestFMIBistroParser:
    bistro_parser = FMIBistroMenuParser()

    def test_fmi_bistro(self, snapshot_json):
        for_generation_path = "src/test/assets/fmi/for-generation/calendar_week_2023_{calendar_week}.txt"
        menus = {}
        for calendar_week in range(21, 23):
            text = file_util.load_txt(for_generation_path.format(calendar_week=calendar_week))
            menus.update(self.bistro_parser.get_menus(text, 2023, calendar_week))
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, Canteen.FMI_BISTRO, True)
            generated = file_util.load_ordered_json(os.path.join(temp_dir, "combined", "combined.json"))
            assert generated == snapshot_json


class TestMedizinerMensaParser:
    mediziner_mensa_parser = MedizinerMensaMenuParser()

    def test_mediziner_mensa(self, snapshot_json):
        # parse the menu
        for calendar_week in [44, 47]:
            for_generation = file_util.load_txt(
                f"src/test/assets/mediziner-mensa/for-generation/week_2018_{calendar_week}.txt",
            )
            menus = self.mediziner_mensa_parser.get_menus(
                for_generation,
                2018,
                calendar_week,
            )
            assert menus is not None
            if not menus:
                return
            weeks = Week.to_weeks(menus)

            # create temp dir for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                # store output in the tempdir
                main.jsonify(weeks, temp_dir, Canteen.MEDIZINER_MENSA, True)
                # open the generated file
                generated = file_util.load_ordered_json(os.path.join(temp_dir, "combined", "combined.json"))
                assert generated == snapshot_json


class TestStraubingMensaMenuParser:
    straubing_mensa_parser = StraubingMensaMenuParser()

    def test_straubing_mensa(self, snapshot_json):
        for calendar_week in [16, 17]:
            with open(f"src/test/assets/straubing/for-generation/{calendar_week}.csv", encoding="cp1252") as f:
                for_generation = f.read()

            rows = self.straubing_mensa_parser.parse_csv(for_generation)

            menus = self.straubing_mensa_parser.parse_menu(rows)
            weeks = Week.to_weeks(menus)

            # create temp dir for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                # store output in the tempdir
                main.jsonify(weeks, temp_dir, Canteen.MENSA_STRAUBING, True)
                # open the generated file
                generated = file_util.load_ordered_json(os.path.join(temp_dir, "2022", f"{calendar_week}.json"))
                assert generated == snapshot_json
