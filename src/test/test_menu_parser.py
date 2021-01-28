# -*- coding: utf-8 -*-
import json
import os
import tempfile
import unittest
from datetime import date

from lxml import html  # nosec: https://github.com/TUM-Dev/eat-api/issues/19

import src.main as main
from src.entities import Week
from src.menu_parser import (
    FMIBistroMenuParser,
    IPPBistroMenuParser,
    MedizinerMensaMenuParser,
    MenuParser,
    StudentenwerkMenuParser,
)


class MenuParserTest(unittest.TestCase):
    def test_get_date(self):
        self.assertEqual(date(2017, 10, 30), MenuParser.get_date(2017, 44, 1))
        self.assertEqual(date(2018, 1, 1), MenuParser.get_date(2018, 1, 1))
        self.assertEqual(date(2019, 1, 7), MenuParser.get_date(2019, 2, 1))


class StudentenwerkMenuParserTest(unittest.TestCase):
    studentenwerk_menu_parser = StudentenwerkMenuParser()

    with open("src/test/assets/studentenwerk/in/speiseplan_mensa_garching_old.html") as speiseplan_mensa_garching_old:
        menu_html_mensa_garching_old = html.fromstring(speiseplan_mensa_garching_old.read())
    with open("src/test/assets/studentenwerk/in/speiseplan_mensa_garching_new.html") as speiseplan_mensa_garching_new:
        menu_html_mensa_garching_new = html.fromstring(speiseplan_mensa_garching_new.read())
    with open(
        "src/test/assets/studentenwerk/in/speiseplan_mensa_garching_old_wrong_date_format.html",
    ) as speiseplan_mensa_garching_old_wrong_date_format:
        menu_html_mensa_garching_old_wrong_date_format = html.fromstring(
            speiseplan_mensa_garching_old_wrong_date_format.read(),
        )
    with open(
        "src/test/assets/studentenwerk/in/speiseplan_stubistro_großhadern.html",
    ) as speiseplan_stubistro_grosshadern:
        menu_html_stubistro_grosshadern = html.fromstring(speiseplan_stubistro_grosshadern.read())
    with open("src/test/assets/studentenwerk/in/speiseplan_mensa_arcisstrasse.html") as speiseplan_mensa_arcisstrasse:
        menu_html_mensa_arcisstrasse = html.fromstring(speiseplan_mensa_arcisstrasse.read())

    def test_studentenwerk_mensa_garching_old(self):
        # parse the menu
        menus = self.studentenwerk_menu_parser.get_menus(self.menu_html_mensa_garching_old, "mensa-garching")
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "mensa-garching", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/studentenwerk/out/speiseplan_mensa_garching_old.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    def test_studentenwerk_mensa_garching_new(self):
        # parse the menu
        menus = self.studentenwerk_menu_parser.get_menus(self.menu_html_mensa_garching_new, "mensa-garching")
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "mensa-garching", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/studentenwerk/out/speiseplan_mensa_garching_new.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    def test_studentenwerk_mensa_garching_old_wrong_date_format(self):
        # parse the menu
        menus = self.studentenwerk_menu_parser.get_menus(
            self.menu_html_mensa_garching_old_wrong_date_format,
            "mensa-garching",
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "mensa-garching", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open(
                    "src/test/assets/studentenwerk/out/speiseplan_mensa_garching_old_wrong_date_format.json",
                    "r",
                ) as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    def test_studentenwerk_stubistro_grosshadern(self):
        # parse the menu
        menus = self.studentenwerk_menu_parser.get_menus(self.menu_html_stubistro_grosshadern, "stubistro-großhadern")
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "stubistro-großhadern", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/studentenwerk/out/speiseplan_stubistro_großhadern.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    def test_studentenwerk_mensa_arcisstrasse(self):
        # parse the menu
        menus = self.studentenwerk_menu_parser.get_menus(self.menu_html_mensa_arcisstrasse, "mensa-arcisstr")
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "mensa-arcisstr", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/studentenwerk/out/speiseplan_mensa_arcisstrasse.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    def test_should_ignore_day_when_date_of_the_day_is_in_a_wrong_format(self):
        menucount = len(
            self.studentenwerk_menu_parser.get_menus(
                self.menu_html_mensa_garching_old_wrong_date_format,
                "mensa-garching",
            ),
        )
        self.assertEqual(22, menucount)

    def test_should_return_weeks_when_converting_menu_to_week_objects(self):
        menus = self.studentenwerk_menu_parser.get_menus(self.menu_html_mensa_garching_old, "mensa-garching")
        weeks_actual = Week.to_weeks(menus)
        length_weeks_actual = len(weeks_actual)

        self.assertEqual(5, length_weeks_actual)
        for calendar_week in weeks_actual:
            week = weeks_actual[calendar_week]
            week_length = len(week.days)
            # calendar weeks 15 and 16 have one day less, because of a holiday
            if calendar_week in [15, 16]:
                self.assertEqual(4, week_length)
            else:
                self.assertEqual(5, week_length)

    def order_json_objects(self, obj):
        """
        Recusively orders all elemts in a Json object.
        Source:
        https://stackoverflow.com/questions/25851183/how-to-compare-two-json-objects-with-the-same-elements-in-a-different-order-equa
        """
        if isinstance(obj, dict):
            return sorted((k, self.order_json_objects(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.order_json_objects(x) for x in obj)
        return obj

    def test_should_convert_week_to_json(self):
        with open("src/test/assets/studentenwerk/out/speiseplan_mensa_garching_kw2017-13.json") as data_file:
            week_2017_13 = json.load(data_file)
        with open("src/test/assets/studentenwerk/out/speiseplan_mensa_garching_kw2017-14.json") as data_file:
            week_2017_14 = json.load(data_file)
        with open("src/test/assets/studentenwerk/out/speiseplan_mensa_garching_kw2017-15.json") as data_file:
            week_2017_15 = json.load(data_file)
        with open("src/test/assets/studentenwerk/out/speiseplan_mensa_garching_kw2017-16.json") as data_file:
            week_2017_16 = json.load(data_file)
        with open("src/test/assets/studentenwerk/out/speiseplan_mensa_garching_kw2017-17.json") as data_file:
            week_2017_17 = json.load(data_file)

        menus = self.studentenwerk_menu_parser.get_menus(self.menu_html_mensa_garching_old, "mensa-garching")
        weeks = Week.to_weeks(menus)
        week_2017_13_actual = json.loads(weeks[13].to_json())
        week_2017_14_actual = json.loads(weeks[14].to_json())
        week_2017_15_actual = json.loads(weeks[15].to_json())
        week_2017_16_actual = json.loads(weeks[16].to_json())
        week_2017_17_actual = json.loads(weeks[17].to_json())

        self.assertEqual(self.order_json_objects(week_2017_13_actual), self.order_json_objects(week_2017_13))
        self.assertEqual(self.order_json_objects(week_2017_14_actual), self.order_json_objects(week_2017_14))
        self.assertEqual(self.order_json_objects(week_2017_15_actual), self.order_json_objects(week_2017_15))
        self.assertEqual(self.order_json_objects(week_2017_16_actual), self.order_json_objects(week_2017_16))
        self.assertEqual(self.order_json_objects(week_2017_17_actual), self.order_json_objects(week_2017_17))

    """
    # just for generating reference json files
    def test_gen_file(self):
        # parse the menu
        menus = self.studentenwerk_menu_parser.get_menus(self.menu_html_mensa_garching_old, "mensa-garching")
        weeks = Week.to_weeks(menus)
        main.jsonify(weeks, "/tmp/eat-api_test_output", "mensa-garching", True)
    """


class FMIBistroParserTest(unittest.TestCase):
    bistro_parser = FMIBistroMenuParser()

    with open("src/test/assets/fmi/in/Garching-Speiseplan_KW44_2017.txt", "r") as menu_kw_44_2017:
        menu_kw_44_2017_txt = menu_kw_44_2017.read()
    menu_kw_44_2017_year = 2017
    menu_kw_44_2017_week_number = 44

    with open("src/test/assets/fmi/in/Garching-Speiseplan_KW45_2017.txt", "r") as menu_kw_45_2017:
        menu_kw_45_2017_txt = menu_kw_45_2017.read()
    menu_kw_45_2017_year = 2017
    menu_kw_45_2017_week_number = 45

    def test_fmi_bistro_kw_44_2017(self):
        # parse the menu
        menus = self.bistro_parser.get_menus(
            self.menu_kw_44_2017_txt,
            self.menu_kw_44_2017_year,
            self.menu_kw_44_2017_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "fmi-bistro", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/fmi/out/menu_kw_44_2017.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    def test_fmi_bistro_kw_45_2017(self):
        # parse the menu
        menus = self.bistro_parser.get_menus(
            self.menu_kw_45_2017_txt,
            self.menu_kw_45_2017_year,
            self.menu_kw_45_2017_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "fmi-bistro", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/fmi/out/menu_kw_45_2017.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    """
    # just for generating reference json files
    def test_gen_file(self):
        # parse the menu
        menus = self.bistro_parser.get_menus(
            self.menu_kw_45_2017_txt, self.menu_kw_45_2017_year, self.menu_kw_45_2017_week_number
        )
        weeks = Week.to_weeks(menus)
        main.jsonify(weeks, "/tmp/eat-api_test_output", "fmi-bistro", True)
    """


class IPPBistroParserTest(unittest.TestCase):
    ipp_parser = IPPBistroMenuParser()

    with open("src/test/assets/ipp/in/menu_kw_47_2017.txt", "r") as menu_kw_47_2017:
        menu_kw_47_2017_txt = menu_kw_47_2017.read()
    menu_kw_47_2017_year = 2017
    menu_kw_47_2017_week_number = 47

    with open("src/test/assets/ipp/in/menu_kw_48_2017.txt", "r") as menu_kw_48_2017:
        menu_kw_48_2017_txt = menu_kw_48_2017.read()
    menu_kw_48_2017_year = 2017
    menu_kw_48_2017_week_number = 48

    def test_ipp_bistro_kw_47_2017(self):
        # parse the menu
        menus = self.ipp_parser.get_menus(
            self.menu_kw_47_2017_txt,
            self.menu_kw_47_2017_year,
            self.menu_kw_47_2017_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "ipp-bistro", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/ipp/out/menu_kw_47_2017.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    def test_ipp_bistro_kw_48_2017(self):
        # parse the menu
        menus = self.ipp_parser.get_menus(
            self.menu_kw_48_2017_txt,
            self.menu_kw_48_2017_year,
            self.menu_kw_48_2017_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "ipp-bistro", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/ipp/out/menu_kw_48_2017.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    # Test Cases with holidays

    # Two holidays (Mon & Tue)
    with open("src/test/assets/ipp/in/menu_kw_18_2018.txt", "r") as menu_kw_18_2018:
        menu_kw_18_2018_txt = menu_kw_18_2018.read()
    menu_kw_18_2018_year = 2018
    menu_kw_18_2018_week_number = 18

    def test_ipp_bistro_kw_18_2018_closed_monday_tuesday(self):
        # parse the menu
        menus = self.ipp_parser.get_menus(
            self.menu_kw_18_2018_txt,
            self.menu_kw_18_2018_year,
            self.menu_kw_18_2018_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "ipp-bistro", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/ipp/out/menu_kw_18_2018.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    # One holiday (Thu)
    with open("src/test/assets/ipp/in/menu_kw_19_2018.txt", "r") as menu_kw_19_2018:
        menu_kw_19_2018_txt = menu_kw_19_2018.read()
    menu_kw_19_2018_year = 2018
    menu_kw_19_2018_week_number = 19

    def test_ipp_bistro_kw_19_2018_closed_thursday(self):
        # parse the menu
        menus = self.ipp_parser.get_menus(
            self.menu_kw_19_2018_txt,
            self.menu_kw_19_2018_year,
            self.menu_kw_19_2018_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "ipp-bistro", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/ipp/out/menu_kw_19_2018.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    # "Überraschungsmenü" and "Geschlossen" in first line of table
    with open("src/test/assets/ipp/in/menu_kw_22_2019.txt", "r") as menu_kw_22_2019:
        menu_kw_22_2019_txt = menu_kw_22_2019.read()
    menu_kw_22_2019_year = 2019
    menu_kw_22_2019_week_number = 22

    def test_ipp_bistro_kw_22_2019_closed_thursday(self):
        # parse the menu
        menus = self.ipp_parser.get_menus(
            self.menu_kw_22_2019_txt,
            self.menu_kw_22_2019_year,
            self.menu_kw_22_2019_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "ipp-bistro", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/ipp/out/menu_kw_22_2019.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    """
    # just for generating reference json files
    def test_gen_file(self):
        # parse the menu
        menus = self.ipp_parser.get_menus(
            self.menu_kw_22_2019_txt,
            self.menu_kw_22_2019_year,
            self.menu_kw_22_2019_week_number,
        )
        weeks = Week.to_weeks(menus)
        main.jsonify(weeks, "/tmp/eat-api_test_output", "ipp-bistro", True)
    """


class MedizinerMensaParserTest(unittest.TestCase):
    mediziner_mensa_parser = MedizinerMensaMenuParser()

    with open("src/test/assets/mediziner-mensa/in/menu_kw_44_2018.txt", "r") as menu_kw_44_2018:
        menu_kw_44_2018_txt = menu_kw_44_2018.read()
    menu_kw_44_2018_year = 2018
    menu_kw_44_2018_week_number = 44

    with open("src/test/assets/mediziner-mensa/in/menu_kw_47_2018.txt", "r") as menu_kw_47_2018:
        menu_kw_47_2018_txt = menu_kw_47_2018.read()
    menu_kw_47_2018_year = 2018
    menu_kw_47_2018_week_number = 47

    def test_mediziner_mensa_kw_44_2018(self):
        # parse the menu
        menus = self.mediziner_mensa_parser.get_menus(
            self.menu_kw_44_2018_txt,
            self.menu_kw_44_2018_year,
            self.menu_kw_44_2018_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "mediziner-mensa", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/mediziner-mensa/out/menu_kw_44_2018.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    def test_mediziner_mensa_kw_47_2018(self):
        # parse the menu
        menus = self.mediziner_mensa_parser.get_menus(
            self.menu_kw_47_2018_txt,
            self.menu_kw_47_2018_year,
            self.menu_kw_47_2018_week_number,
        )
        weeks = Week.to_weeks(menus)

        # create temp dir for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # store output in the tempdir
            main.jsonify(weeks, temp_dir, "mediziner-mensa", True)
            # open the generated file
            with open(os.path.join(temp_dir, "combined", "combined.json"), "r") as generated:
                # open the reference file
                with open("src/test/assets/mediziner-mensa/out/menu_kw_47_2018.json", "r") as reference:
                    self.assertEqual(json.load(generated), json.load(reference))

    # """
    # just for generating reference json files
    def test_gen_file(self):
        # parse the menu
        menus = self.mediziner_mensa_parser.get_menus(
            self.menu_kw_47_2018_txt,
            self.menu_kw_47_2018_year,
            self.menu_kw_47_2018_week_number,
        )
        weeks = Week.to_weeks(menus)
        main.jsonify(weeks, "/tmp/eat-api_test_output", "mediziner-mensa", True)

    # """
