# -*- coding: utf-8 -*-
# pylint:disable=too-many-lines

import csv
import datetime
import re
import tempfile
import unicodedata
from abc import ABC, abstractmethod
from enum import Enum, auto
from subprocess import call  # nosec: all the inputs is fully defined
from typing import Dict, List, Optional, Pattern, Set, Tuple
from warnings import warn

import requests  # type: ignore
from lxml import html  # nosec: https://github.com/TUM-Dev/eat-api/issues/19

from entities import Canteen, Dish, Label, Menu, Price, Prices, Week
from utils import util


class ParsingError(Exception):
    pass


class MenuParser(ABC):
    """
    Abstract menu parser class.
    """

    canteens: Set[Canteen]
    _label_subclasses: Dict[str, Set[Label]]
    # we use datetime %u, so we go from 1-7
    weekday_positions: Dict[str, int] = {"mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6, "sun": 7}

    @staticmethod
    def get_date(year: int, week_number: int, day: int) -> datetime.date:
        # get date from year, week number and current weekday
        # https://stackoverflow.com/questions/17087314/get-date-from-week-number
        # but use the %G for year and %V for the week since in Germany we use ISO 8601 for week numbering
        date_format: str = "%G-W%V-%u"
        date_str: str = "%d-W%d-%d"

        return datetime.datetime.strptime(date_str % (year, week_number, day), date_format).date()

    @abstractmethod
    def parse(self, canteen: Canteen) -> Optional[Dict[datetime.date, Menu]]:
        pass

    @classmethod
    def _parse_label(cls, labels_str: str) -> Set[Label]:
        labels: Set[Label] = set()
        split_values: List[str] = labels_str.strip().split(",")
        for value in split_values:
            stripped = value.strip()
            if not stripped.isspace():
                labels |= cls._label_subclasses.get(stripped, set())
        Label.add_supertype_labels(labels)
        return labels


class StudentenwerkMenuParser(MenuParser):
    # Canteens:
    canteens = {
        Canteen.MENSA_ARCISSTR,
        Canteen.MENSA_GARCHING,
        Canteen.MENSA_LEOPOLDSTR,
        Canteen.MENSA_LOTHSTR,
        Canteen.MENSA_MARTINSRIED,
        Canteen.MENSA_PASING,
        Canteen.MENSA_WEIHENSTEPHAN,
        Canteen.STUBISTRO_ARCISSTR,
        Canteen.STUBISTRO_GOETHESTR,
        Canteen.STUBISTRO_BUTENANDSTR,
        Canteen.STUBISTRO_ROSENHEIM,
        Canteen.STUBISTRO_SCHELLINGSTR,
        Canteen.STUBISTRO_MARTINSRIED,
        Canteen.STUCAFE_ADALBERTSTR,
        Canteen.STUCAFE_AKADEMIE_WEIHENSTEPHAN,
        Canteen.STUCAFE_WEIHENSTEPHAN_MAXIMUS,
        Canteen.STUCAFE_BOLTZMANNSTR,
        Canteen.STUCAFE_CONNOLLYSTR,
        Canteen.STUCAFE_GARCHING,
        Canteen.STUCAFE_KARLSTR,
        Canteen.STUCAFE_PASING,
    }

    # Prices taken from: https://www.studierendenwerk-muenchen-oberbayern.de/mensa/mensa-preise/

    # Base price for sausage, meat and fish. The price is the same for all meals except pizza
    # only the first values is used in the triplets which do not contain pizza.
    class SelfServiceBasePriceType(Enum):
        VEGETARIAN_SOUP_STEW = (0, 0, 0)
        SAUSAGE = (0.5, 0.5, 0.5)
        MEAT = (1.0, 1.0, 1.0)
        FISH = (1.5, 1.5, 1.5)
        PIZZA_VEGIE = (4.0, 4.5, 5.0)
        PIZZA_MEAT = (4.5, 5.0, 5.5)

        def __init__(self, p1, p2, p3):
            self.price = (p1, p2, p3)

    # Meet and vegetarian base prices for Students, Staff, Guests
    class SelfServicePricePerUnitType(Enum):
        CLASSIC = 0.80, 1.00, 1.35
        SOUP_STEW = 0.33, 0.65, 1.35
        PIZZA = 0.0, 0.0, 0.0

        def __init__(self, students: float, staff: float, guests: float):
            self.students = students
            self.staff = staff
            self.guests = guests
            self.unit = "100g"

    _label_subclasses: Dict[str, Set[Label]] = {
        "GQB": {Label.BAVARIA},
        "MSC": {Label.MSC},
        "1": {Label.DYESTUFF},
        "2": {Label.PRESERVATIVES},
        "3": {Label.ANTIOXIDANTS},
        "4": {Label.FLAVOR_ENHANCER},
        "5": {Label.SULPHURS},
        "6": {Label.DYESTUFF},
        "7": {Label.WAXED},
        "8": {Label.PHOSPATES},
        "9": {Label.SWEETENERS},
        "10": {Label.PHENYLALANINE},
        "11": {Label.SWEETENERS},
        "13": {Label.COCOA_CONTAINING_GREASE},
        "14": {Label.GELATIN},
        "99": {Label.ALCOHOL},
        "f": {Label.VEGETARIAN},
        "v": {Label.VEGAN},
        "S": {Label.PORK},
        "R": {Label.BEEF},
        "K": {Label.VEAL},
        "Kn": {Label.GARLIC},
        "Ei": {Label.CHICKEN_EGGS},
        "En": {Label.PEANUTS},
        "Fi": {Label.FISH},
        "Gl": {Label.GLUTEN},
        "GlW": {Label.WHEAT},
        "GlR": {Label.RYE},
        "GlG": {Label.BARLEY},
        "GlH": {Label.OAT},
        "GlD": {Label.SPELT},
        "Kr": {Label.SHELLFISH},
        "Lu": {Label.LUPIN},
        "Mi": {Label.MILK, Label.LACTOSE},
        "Sc": {Label.SHELLFISH},
        "ScM": {Label.ALMONDS},
        "ScH": {Label.HAZELNUTS},
        "ScW": {Label.WALNUTS},
        "ScC": {Label.CASHEWS},
        "ScP": {Label.PISTACHIOES},
        "Se": {Label.SESAME},
        "Sf": {Label.MUSTARD},
        "Sl": {Label.CELERY},
        "So": {Label.SOY},
        "Sw": {Label.SULPHURS, Label.SULFITES},
        "Wt": {Label.MOLLUSCS},
    }

    # Students, Staff, Guests
    # Looks like those are the fallback prices
    prices_mensa_weihenstephan_mensa_lothstrasse: Dict[str, Tuple[Price, Price, Price]] = {
        "Tagesgericht 1": Prices(Price(1.00), Price(2.25), Price(3.10)),
        "Tagesgericht 2": Prices(Price(1.70), Price(2.50), Price(3.50)),
        "Tagesgericht 3": Prices(Price(2.05), Price(2.85), Price(3.90)),
        "Tagesgericht 4": Prices(Price(2.55), Price(3.20), Price(4.30)),
        "Suppe": Prices(Price(0.60), Price(0.70), Price(1.10)),
        "Stärkebeilagen": Prices(Price(0.65), Price(0.90), Price(1.25)),
        "Beilage": Prices(Price(0.65), Price(0.90), Price(1.25)),
        "Salatbuffet": Prices(Price(0, 0.80, "100g"), Price(0, 1.00, "100g"), Price(0, 1.35, "100g")),
        "Obst": Prices(Price(0.85), Price(0.85), Price(0.85)),
        "Bio-/Aktionsgericht 1": Prices(Price(1.70), Price(2.50), Price(3.50)),
        "Bio-/Aktionsgericht 2": Prices(Price(2.05), Price(2.85), Price(3.90)),
        "Bio-/Aktionsgericht 3": Prices(Price(2.55), Price(3.20), Price(4.30)),
        "Bio-/Aktionsgericht 4": Prices(Price(2.75), Price(3.55), Price(4.70)),
        "Bio-/Aktionsgericht 5": Prices(Price(2.95), Price(3.90), Price(5.10)),
        "Bio-/Aktionsgericht 6": Prices(Price(3.15), Price(4.25), Price(5.50)),
        "Bio-/Aktionsgericht 7": Prices(Price(3.35), Price(4.60), Price(5.90)),
        "Bio-/Aktionsgericht 8": Prices(Price(3.65), Price(4.95), Price(6.30)),
        "Bio-/Aktionsgericht 9": Prices(Price(4.15), Price(5.30), Price(6.70)),
        "Bio-/Aktionsgericht 10": Prices(Price(4.65), Price(5.65), Price(7.10)),
        "Bio-/Aktionsbeilage 1": Prices(Price(0.65), Price(0.90), Price(1.30)),
        "Bio-/Aktionsbeilage 2": Prices(Price(0.80), Price(1.05), Price(1.50)),
        "Bio-/Aktionsbeilage 3": Prices(Price(0.90), Price(1.25), Price(1.70)),
        "Bio-/Aktionsbeilage 4": Prices(Price(1.10), Price(1.45), Price(2.00)),
        "Aktionsbeilage 6": Prices(Price(1.50), Price(1.70), Price(2.30)),
    }

    @staticmethod
    def __get_self_service_prices(
        base_price_type: SelfServiceBasePriceType,
        price_per_unit_type: SelfServicePricePerUnitType,
    ) -> Prices:
        students: Price = Price(
            base_price_type.price[0],
            price_per_unit_type.students,
            price_per_unit_type.unit,
        )
        staff: Price = Price(
            base_price_type.price[1],
            price_per_unit_type.staff,
            price_per_unit_type.unit,
        )
        guests: Price = Price(
            base_price_type.price[2],
            price_per_unit_type.guests,
            price_per_unit_type.unit,
        )
        return Prices(students, staff, guests)

    @staticmethod
    def __get_price(canteen: Canteen, dish: Tuple[str, str, str, str, str], dish_name: str) -> Prices:
        if canteen in [Canteen.MENSA_WEIHENSTEPHAN, Canteen.MENSA_LOTHSTR]:
            return StudentenwerkMenuParser.prices_mensa_weihenstephan_mensa_lothstrasse.get(dish[0], Prices())

        if dish[0] == "Studitopf":  # Soup or Stew
            price_per_unit_type = StudentenwerkMenuParser.SelfServicePricePerUnitType.SOUP_STEW
        else:
            price_per_unit_type = StudentenwerkMenuParser.SelfServicePricePerUnitType.CLASSIC

        if dish[0] != "Studitopf" and dish[4] == "0":  # Non-Vegetarian
            if "Fi" in dish[2]:
                base_price_type = StudentenwerkMenuParser.SelfServiceBasePriceType.FISH
            # TODO: Find better way to distinguish between sausage and meat
            elif "wurst" in dish_name.lower() or "würstchen" in dish_name.lower():
                base_price_type = StudentenwerkMenuParser.SelfServiceBasePriceType.SAUSAGE
            else:
                base_price_type = StudentenwerkMenuParser.SelfServiceBasePriceType.MEAT
        else:
            base_price_type = StudentenwerkMenuParser.SelfServiceBasePriceType.VEGETARIAN_SOUP_STEW

        if dish[0] == "Pizza":
            price_per_unit_type = StudentenwerkMenuParser.SelfServicePricePerUnitType.PIZZA
            if dish[4] == "0":
                base_price_type = StudentenwerkMenuParser.SelfServiceBasePriceType.PIZZA_MEAT
            else:
                base_price_type = StudentenwerkMenuParser.SelfServiceBasePriceType.PIZZA_VEGIE
        return StudentenwerkMenuParser.__get_self_service_prices(base_price_type, price_per_unit_type)

    base_url: str = "https://www.studierendenwerk-muenchen-oberbayern.de/mensa/speiseplan/speiseplan_{url_id}_-de.html"

    def parse(self, canteen: Canteen) -> Optional[Dict[datetime.date, Menu]]:
        menus = {}
        page_link: str = self.base_url.format(url_id=canteen.url_id)
        page: requests.Response = requests.get(page_link, timeout=10.0)
        if page.ok:
            try:
                tree: html.Element = html.fromstring(page.content)
                html_menus: List[html.Element] = self.get_daily_menus_as_html(tree)
                for html_menu in html_menus:
                    # this solves some weird reference? issue where tree.xpath will subsequently always use
                    # the first element despite looping through seemingly separate elements
                    html_menu = html.fromstring(html.tostring(html_menu))
                    menu = self.get_menu(html_menu, canteen)
                    if menu:
                        menus[menu.menu_date] = menu
                # pylint: disable=broad-except
            except Exception as e:
                print(f"Exception while parsing menu. Skipping current date. Exception args: {e.args}")
        # pylint: enable=broad-except
        return menus

    def get_menu(self, page: html.Element, canteen: Canteen) -> Optional[Menu]:
        date = self.extract_date_from_html(page)
        dishes: List[Dish] = self.__parse_dishes(page, canteen)
        menu: Menu = Menu(date, dishes)
        return menu

    # public for testing
    @staticmethod
    def extract_date_from_html(tree: html.Element) -> Optional[datetime.date]:
        date_str: str = tree.xpath("//div[@class='c-schedule__item']//strong/text()")[0]
        try:
            date: datetime.date = util.parse_date(date_str)
            return date
        except ValueError:
            warn(f"Error during parsing date from html page. Problematic date: {date_str}")
            return None

    # public for testing
    @staticmethod
    def get_daily_menus_as_html(tree: html.Element) -> List[html.Element]:
        # obtain all daily menus found in the passed html page by xpath query
        daily_menus: List[html.Element] = tree.xpath("//div[@class='c-schedule__item']")
        return daily_menus

    @staticmethod
    def __parse_dishes(menu_html: html.Element, canteen: Canteen) -> List[Dish]:
        # obtain the names of all dishes in a passed menu
        dish_names: List[str] = [dish.rstrip() for dish in menu_html.xpath("//p[@class='c-menu-dish__title']/text()")]
        # make duplicates unique by adding (2), (3) etc. to the names
        dish_names = util.make_duplicates_unique(dish_names)
        # obtain the types of the dishes (e.g. 'Tagesgericht 1')
        dish_types: List[str] = []
        current_type = ""
        for type_ in menu_html.xpath("//span[@class='stwm-artname']"):
            if type_.text:
                current_type = type_.text
            dish_types += [current_type]
        # obtain all labels
        dish_markers_additional: List[str] = menu_html.xpath(
            "//li[contains(@class, 'c-menu-dish-list__item  u-clearfix  "
            "clearfix  js-menu__list-item')]/@data-essen-zusatz",
        )
        dish_markers_allergen: List[str] = menu_html.xpath(
            "//li[contains(@class, 'c-menu-dish-list__item  u-clearfix  "
            "clearfix  js-menu__list-item')]/@data-essen-allergene",
        )
        dish_markers_type: List[str] = menu_html.xpath(
            "//li[contains(@class, 'c-menu-dish-list__item  u-clearfix  "
            "clearfix  js-menu__list-item')]/@data-essen-typ",
        )
        dish_markers_meetless: List[str] = menu_html.xpath(
            "//li[contains(@class, 'c-menu-dish-list__item  u-clearfix  "
            "clearfix  js-menu__list-item')]/@data-essen-fleischlos",
        )

        # create dictionary out of dish name and dish type
        dishes_dict: Dict[str, Tuple[str, str, str, str, str]] = {}
        dishes_tup: zip = zip(
            dish_names,
            dish_types,
            dish_markers_additional,
            dish_markers_allergen,
            dish_markers_type,
            dish_markers_meetless,
        )
        for (
            dish_name,
            dish_type,
            dish_marker_additional,
            dish_marker_allergen,
            dish_marker_type,
            dish_marker_meetless,
        ) in dishes_tup:
            dishes_dict[dish_name] = (
                dish_type,
                dish_marker_additional,
                dish_marker_allergen,
                dish_marker_type,
                dish_marker_meetless,
            )

        # create Dish objects with correct prices; if prices is not available, -1 is used instead
        dishes: List[Dish] = []
        for name in dishes_dict:
            # parse labels
            labels = set()
            labels |= StudentenwerkMenuParser._parse_label(dishes_dict[name][1])
            labels |= StudentenwerkMenuParser._parse_label(dishes_dict[name][2])
            labels |= StudentenwerkMenuParser._parse_label(dishes_dict[name][3])
            StudentenwerkMenuParser.__add_diet(labels, dishes_dict[name][4])
            # do not price side dishes
            prices: Prices
            if dishes_dict[name][0] == "Beilagen":
                # set classic prices without any base price
                prices = StudentenwerkMenuParser.__get_self_service_prices(
                    StudentenwerkMenuParser.SelfServiceBasePriceType.VEGETARIAN_SOUP_STEW,
                    StudentenwerkMenuParser.SelfServicePricePerUnitType.CLASSIC,
                )
            else:
                # find prices
                prices = StudentenwerkMenuParser.__get_price(canteen, dishes_dict[name], name)
            dishes.append(Dish(name, prices, labels, dishes_dict[name][0]))
        return dishes

    @staticmethod
    def __add_diet(labels: Set[Label], diet_str: str) -> None:
        if diet_str == "0":
            if Label.FISH not in labels:
                labels |= {Label.MEAT}
        elif diet_str == "1":
            labels |= {Label.VEGETARIAN}
        elif diet_str == "2":
            labels |= {Label.VEGAN}
        Label.add_supertype_labels(labels)


class FMIBistroMenuParser(MenuParser):
    url = "https://www.wilhelm-gastronomie.de/.cm4all/mediadb/Speiseplan_Garching_KW{calendar_week}_{year}.pdf"

    canteens = {Canteen.FMI_BISTRO}

    class DishType(Enum):
        SOUP = auto()
        MEAT = auto()
        VEGETARIAN = auto()
        VEGAN = auto()

    _label_subclasses: Dict[str, Set[Label]] = {
        "a": {Label.GLUTEN},
        "aW": {Label.WHEAT},
        "aR": {Label.RYE},
        "aG": {Label.BARLEY},
        "aH": {Label.OAT},
        "aD": {Label.SPELT},
        "aHy": {Label.HYBRIDS},
        "b": {Label.SHELLFISH},
        "c": {Label.CHICKEN_EGGS},
        "d": {Label.FISH},
        "e": {Label.PEANUTS},
        "f": {Label.SOY},
        "g": {Label.MILK},
        "u": {Label.LACTOSE},
        "h": {Label.SHELL_FRUITS},
        "hMn": {Label.ALMONDS},
        "hH": {Label.HAZELNUTS},
        "hW": {Label.WALNUTS},
        "hK": {Label.CASHEWS},
        "hPe": {Label.PECAN},
        "hPi": {Label.PISTACHIOES},
        "hQ": {Label.MACADAMIA},
        "i": {Label.CELERY},
        "j": {Label.MUSTARD},
        "k": {Label.SESAME},
        "l": {Label.SULFITES, Label.SULPHURS},
        "m": {Label.LUPIN},
        "n": {Label.MOLLUSCS},
    }

    def parse(self, canteen: Canteen) -> Optional[Dict[datetime.date, Menu]]:
        today = datetime.date.today()
        years_and_calendar_weeks: List[Tuple[int, int, int]] = [
            today.isocalendar(),
            (today + datetime.timedelta(days=7)).isocalendar(),
        ]
        menus = {}
        for year, calendar_week, _ in years_and_calendar_weeks:
            # get pdf
            page = requests.get(self.url.format(calendar_week=calendar_week, year=year), timeout=10.0)
            if page.status_code == 200:
                with tempfile.NamedTemporaryFile() as temp_pdf:
                    # download pdf
                    temp_pdf.write(page.content)
                    with tempfile.NamedTemporaryFile() as temp_txt:
                        # convert pdf to text by calling pdftotext
                        call(
                            ["pdftotext", "-layout", temp_pdf.name, temp_txt.name],
                        )  # nosec: all input is fully defined
                        with open(temp_txt.name, "r", encoding="utf-8") as myfile:
                            # read generated text file
                            data = myfile.read()
                            parsed_menus = self.get_menus(data, year, calendar_week)
                            if parsed_menus is not None:
                                menus.update(parsed_menus)
        return menus

    def get_menus(self, text: str, year: int, calendar_week: int) -> Dict[datetime.date, Menu]:
        menus = {}

        lines, menu_end, menu_start = self.__get_relevant_text(text)

        for date in Week.get_non_weekend_days_for_calendar_week(year, calendar_week):
            dishes = []
            dish_title_parts = []
            dish_type_iterator = iter(FMIBistroMenuParser.DishType)

            for line in lines:
                if "€" not in line:
                    dish_title_part = self.__extract_dish_title_part(line, date.weekday())
                    if dish_title_part:
                        dish_title_parts += [dish_title_part]
                else:
                    try:
                        dish_type = next(dish_type_iterator)
                    except StopIteration as e:
                        raise ParsingError(
                            f"Only 4 lines in the lines from {menu_start}-{menu_end} are expected to"
                            f" contain the '€' sign.",
                        ) from e
                    label_str_and_price_optional = self.__get_label_str_and_price(date.weekday(), line)
                    if label_str_and_price_optional is None:
                        # no menu for that day
                        break
                    label_str, price = label_str_and_price_optional
                    dish_prices = Prices(Price(price), Price(price), Price(price + 0.8))
                    labels = FMIBistroMenuParser._parse_label(label_str)

                    # merge title lines and replace subsequent whitespaces with single " "
                    dish_title = re.sub(r"\s+", " ", " ".join(dish_title_parts))
                    dishes += [Dish(dish_title, dish_prices, labels, str(dish_type))]

                    dish_title_parts = []
            if dishes:
                menus[date] = Menu(date, dishes)
        return menus

    def __extract_dish_title_part(self, line: str, weekday_index: int) -> Optional[str]:
        estimated_column_length = 49
        estimated_column_begin = weekday_index * estimated_column_length
        estimated_column_end = min(estimated_column_begin + estimated_column_length, len(line))
        # compensate rounding errors
        if abs(estimated_column_end - len(line)) < 5:
            estimated_column_end = len(line)
        try:
            # cast to str for return type check of pre-commit
            return str(re.findall(r"\S+(?:\s+\S+)*", line[estimated_column_begin:estimated_column_end])[0])
        except IndexError:
            return None

    def __get_relevant_text(self, text: str) -> Tuple[List[str], int, int]:
        ignore_line_words = {
            "",
            "suppe",
            "meat",
            "&",
            "grill",
            "vegan*",
            "veggie",
        }
        ignore_line_regex = r"(\s*" + r"|\s*".join(ignore_line_words) + r"\s*)"

        lines: List[str] = []
        menu_start = 4
        menu_end = -18
        for line in text.splitlines()[menu_start:menu_end]:
            if re.fullmatch(ignore_line_regex, line, re.IGNORECASE):
                continue
            lines += [line[13:]]
        return lines, menu_end, menu_start

    def __get_label_str_and_price(self, column_index: int, line: str) -> Optional[Tuple[str, float]]:
        # match labels or prices
        estimated_column_length = int(len(line) / 5)
        estimated_column_begin = column_index * estimated_column_length
        estimated_column_end = min(estimated_column_begin + estimated_column_length, len(line))
        delta = 15
        try:
            price_str = re.findall(
                r"\d+(?:,\d+)?",
                # pre-commit tool black will reformat the file so that flake8 will complain with E203.
                # However, according to
                # https://black.readthedocs.io/en/stable/faq.html#why-are-flake8-s-e203-and-w503-violated,
                # this is against PEP8
                line[estimated_column_end - delta : min(estimated_column_end + delta, len(line))],  # noqa: E203
            )[0]
        except IndexError:
            return None
        price = float(price_str.replace(",", "."))
        try:
            labels_str = re.findall(
                r"[A-Za-z](?:,[A-Za-z]+)*",
                # pre-commit tool black will reformat the file so that flake8 will complain with E203.
                # However, according to
                # https://black.readthedocs.io/en/stable/faq.html#why-are-flake8-s-e203-and-w503-violated,
                # this is against PEP8
                line[max(estimated_column_begin - delta, 0) : estimated_column_begin + delta],  # noqa: E203
            )[0]
        except IndexError:
            labels_str = ""
        return labels_str, price


class IPPBistroMenuParser(MenuParser):
    canteens = {Canteen.IPP_BISTRO}

    url = "http://konradhof-catering.com/ipp/"
    split_days_regex: Pattern[str] = re.compile(
        r"(Tagessuppe siehe Aushang|Aushang|Aschermittwoch|Feiertag|Geschlossen)",
        re.IGNORECASE,
    )
    split_days_regex_soup_one_line: Pattern[str] = re.compile(
        r"T agessuppe siehe Aushang|Tagessuppe siehe Aushang",
        re.IGNORECASE,
    )
    split_days_regex_soup_two_line: Pattern[str] = re.compile(r"Aushang", re.IGNORECASE)
    split_days_regex_closed: Pattern[str] = re.compile(r"Aschermittwoch|Feiertag|Geschlossen", re.IGNORECASE)
    surprise_without_price_regex: Pattern[str] = re.compile(r"(Überraschungsmenü\s)(\s+[^\s\d]+)")
    """Detects the ‚Überraschungsmenü‘ keyword if it has not a price. The price is expected between the groups."""
    dish_regex: Pattern[str] = re.compile(r"(.+?)(\d+,\d+|\?€)\s€[^)]")

    def parse(self, canteen: Canteen) -> Optional[Dict[datetime.date, Menu]]:
        page = requests.get(self.url, timeout=10.0)
        # get html tree
        tree = html.fromstring(page.content)
        # get url of current pdf menu
        xpath_query = tree.xpath("//a[contains(@title, 'KW_')]/@href")

        if len(xpath_query) < 1:
            return None

        menus = {}
        for pdf_url in xpath_query:
            # Example PDF-name: KW-48_27.11-01.12.10.2017-3.pdf
            pdf_name = pdf_url.split("/")[-1]
            # more examples: https://regex101.com/r/hwdpFx/1
            wn_year_match = re.search(r"KW[^a-zA-Z1-9]*([1-9]+\d*).*\d+\.\d+\.(\d+).*", pdf_name, re.IGNORECASE)
            week_number = int(wn_year_match.group(1)) if wn_year_match else None
            year = int(wn_year_match.group(2)) if wn_year_match else None
            # convert 2-digit year into 4-digit year
            year = 2000 + year if year is not None and len(str(year)) == 2 else year

            with tempfile.NamedTemporaryFile() as temp_pdf:
                # download pdf
                response = requests.get(pdf_url, timeout=10.0)
                temp_pdf.write(response.content)
                with tempfile.NamedTemporaryFile() as temp_txt:
                    # convert pdf to text by calling pdftotext; only convert first page to txt (-l 1)
                    call(
                        ["pdftotext", "-l", "1", "-layout", temp_pdf.name, temp_txt.name],
                    )  # nosec: all input is fully defined
                    with open(temp_txt.name, "r", encoding="utf-8") as myfile:
                        # read generated text file
                        data = myfile.read()
                        parsed_menus = self.get_menus(data, year, week_number)
                        if parsed_menus is not None:
                            menus.update(parsed_menus)

        return menus

    def get_menus(self, text, year, week_number):
        menus = {}
        lines = text.splitlines()
        count = 0
        # remove headline etc.
        for line in lines:
            # Find the line which is the header of the table and includes the day of week
            line_shrink = line.replace(" ", "").replace("\n", "").lower()
            # Note we do not include 'montag' und 'freitag' since they are also used in the line before the table
            # header to indicate the range of the week “Monday … until Friday _”
            if any(x in line_shrink for x in ("dienstag", "mittwoch", "donnerstag")):
                break

            count += 1  # noqa: SIM113

        else:
            warn(
                f"NotImplemented: IPP parsing failed. Menu text is not a weekly menu. First line: '{lines[0]}'",
            )
            return None

        lines = lines[count:]
        weekdays = lines[0]

        # The column detection is done through the string "Tagessuppe siehe Aushang" which is at the beginning of
        # every column. However, due to center alignment the column do not begin at the 'T' character and broader
        # text in the column might be left of this character, which then gets truncated. But the gap between the 'T'
        # and the '€' character of the previous column¹ — the real beginning of the current column — is always three,
        # which will be subtracted here. Monday is the second column, so the value should never become negative
        # although it is handled here.
        # ¹or 'e' of "Internationale Küche" if it is the monday column

        # find lines which match the regex
        # lines[1:] == exclude the weekday line which also can contain `Geschlossen`
        soup_lines_iter = (x for x in lines[1:] if self.split_days_regex.search(x))

        soup_line1 = next(soup_lines_iter)
        soup_line2 = next(soup_lines_iter, "")

        # Sometimes on closed days, the keywords are written instead of the week of day instead of the soup line
        positions1 = [
            (max(a.start() - 3, 0), a.end())
            for a in list(
                re.finditer(self.split_days_regex_closed, weekdays),
            )
        ]

        positions2 = [
            (max(a.start() - 3, 0), a.end())
            for a in list(
                re.finditer(self.split_days_regex_soup_one_line, soup_line1),
            )
        ]
        # In the second line there is just 'Aushang' (two lines "Tagessuppe siehe Aushang" or
        # closed days ("Geschlossen", "Feiertag")
        positions3 = [
            (max(a.start() - 14, 0), a.end() + 3)
            for a in list(
                re.finditer(self.split_days_regex_soup_two_line, soup_line2),
            )
        ]
        # closed days ("Geschlossen", "Feiertag", …) can be in first line and second line
        positions4 = [
            (max(a.start() - 3, 0), a.end())
            for a in list(re.finditer(self.split_days_regex_closed, soup_line1))
            + list(re.finditer(self.split_days_regex_closed, soup_line2))
        ]

        if positions3:  # Two lines "Tagessuppe siehe Aushang"
            soup_line_index = lines.index(soup_line2)
        else:
            soup_line_index = lines.index(soup_line1)

        positions = sorted(positions1 + positions2 + positions3 + positions4)

        if len(positions) != 5:
            warn(
                f"IPP PDF parsing of week {week_number} in year {year} failed. "
                f"Only {len(positions)} of 5 columns detected.",
            )
            return None

        pos_mon = positions[0][0]
        pos_tue = positions[1][0]
        pos_wed = positions[2][0]
        pos_thu = positions[3][0]
        pos_fri = positions[4][0]

        lines_weekdays = {"mon": "", "tue": "", "wed": "", "thu": "", "fri": ""}
        # it must be lines[3:] instead of lines[2:] or else the menus would start with "Preis ab 0,90€" (from the
        # soups) instead of the first menu, if there is a day where the bistro is closed.
        for line in lines[soup_line_index + 3 :]:  # noqa: E203
            lines_weekdays["mon"] += " " + line[pos_mon:pos_tue].replace("\n", " ")
            lines_weekdays["tue"] += " " + line[pos_tue:pos_wed].replace("\n", " ")
            lines_weekdays["wed"] += " " + line[pos_wed:pos_thu].replace("\n", " ")
            lines_weekdays["thu"] += " " + line[pos_thu:pos_fri].replace("\n", " ")
            lines_weekdays["fri"] += " " + line[pos_fri:].replace("\n", " ")

        for key in lines_weekdays:
            # Appends `?€` to „Überraschungsmenü“ if it do not have a price. The second '€' is a separator for the
            # later split
            # pylint:disable=E4702
            lines_weekdays[key] = self.surprise_without_price_regex.sub(r"\g<1>?€ € \g<2>", lines_weekdays[key])
            # get rid of two-character umlauts (e.g. SMALL_LETTER_A+COMBINING_DIACRITICAL_MARK_UMLAUT)
            lines_weekdays[key] = unicodedata.normalize("NFKC", lines_weekdays[key])
            # remove multi-whitespaces
            lines_weekdays[key] = " ".join(lines_weekdays[key].split())
            # pylint:enable=E4702
            # get all dish including name and price
            dish_names_price = re.findall(self.dish_regex, lines_weekdays[key] + " ")
            # create dish types
            # since we have the same dish types every day we can use them if there are 4 dishes available
            if len(dish_names_price) == 4:
                dish_types = ["Veggie", "Traditionelle Küche", "Internationale Küche", "Specials"]
            else:
                dish_types = ["Tagesgericht"] * len(dish_names_price)

            # create labels
            # all dishes have the same ingridients
            # TODO: switch to new label and Canteen enum
            # labels = IngredientsOld("ipp-bistro")
            # labels.parse_labels("Mi,Gl,Sf,Sl,Ei,Se,4")
            # create list of Dish objects
            # see TODO above
            labels: Set[Label] = set()
            dishes = []
            for i, (dish_name, price) in enumerate(dish_names_price):
                price_str: str = price.replace(",", ".").strip()
                price_obj: Optional[Price] = None
                try:
                    price_obj = Price(float(price_str))
                except ValueError:
                    warn(f"Error during parsing price: {price_str}")
                dishes.append(
                    Dish(
                        dish_name.strip(),
                        Prices(price_obj),
                        labels,
                        dish_types[i],
                    ),
                )
            date = self.get_date(year, week_number, self.weekday_positions[key])
            # create new Menu object and add it to dict
            menu = Menu(date, dishes)
            # remove duplicates
            menu.remove_duplicates()
            menus[date] = menu

        return menus


class MedizinerMensaMenuParser(MenuParser):
    canteens = {Canteen.MEDIZINER_MENSA}

    startPageurl = "https://www.sv.tum.de/med/startseite/"
    baseUrl = "https://www.sv.tum.de"
    labels_regex = r"(\s([A-C]|[E-H]|[K-P]|[R-Z]|[1-9])(,([A-C]|[E-H]|[K-P]|[R-Z]|[1-9]))*(\s|\Z))"
    price_regex = r"(\d+(,(\d){2})\s?€)"

    _label_subclasses: Dict[str, Set[Label]] = {
        "1": {Label.DYESTUFF},
        "2": {Label.PRESERVATIVES},
        "3": {Label.ANTIOXIDANTS},
        "4": {Label.FLAVOR_ENHANCER},
        "5": {Label.SULPHURS},
        "6": {Label.DYESTUFF},
        "7": {Label.WAXED},
        "8": {Label.PHOSPATES},
        "9": {Label.SWEETENERS},
        "A": {Label.ALCOHOL},
        "B": {Label.GLUTEN},
        "C": {Label.SHELLFISH},
        "E": {Label.FISH},
        "F": {Label.FISH},
        "G": {Label.POULTRY},
        "H": {Label.PEANUTS},
        "K": {Label.VEAL},
        "L": {Label.LAMB},
        "M": {Label.SOY},
        "N": {Label.MILK, Label.LACTOSE},
        "O": {Label.SHELL_FRUITS},
        "P": {Label.CELERY},
        "R": {Label.BEEF},
        "S": {Label.PORK},
        "T": {Label.MUSTARD},
        "U": {Label.SESAME},
        "V": {Label.SULPHURS, Label.SULFITES},
        "W": {Label.WILD_MEAT},
        "X": {Label.LUPIN},
        "Y": {Label.CHICKEN_EGGS},
        "Z": {Label.MOLLUSCS},
    }

    def parse_dish(self, dish_str):
        labels = set()
        matches = re.findall(self.labels_regex, dish_str)
        while len(matches) > 0:
            for match in matches:
                if len(match) > 0:
                    labels |= MedizinerMensaMenuParser._parse_label(match[0])
            dish_str = re.sub(self.labels_regex, " ", dish_str)
            matches = re.findall(self.labels_regex, dish_str)
        dish_str = re.sub(r"\s+", " ", dish_str).strip()
        dish_str = dish_str.replace(" , ", ", ")

        # price
        dish_price = Prices()
        for match in re.findall(self.price_regex, dish_str):
            if len(match) > 0:
                dish_price = Prices(Price(float(match[0].replace("€", "").replace(",", ".").strip())))
        dish_str = re.sub(self.price_regex, "", dish_str)

        return Dish(dish_str, dish_price, labels, "Tagesgericht")

    def parse(self, canteen: Canteen) -> Optional[Dict[datetime.date, Menu]]:
        page = requests.get(self.startPageurl, timeout=10.0)
        # get html tree
        tree = html.fromstring(page.content)
        # get url of current pdf menu
        xpath_query = tree.xpath("//a[contains(@href, 'Mensaplan/KW_')]/@href")

        if len(xpath_query) != 1:
            return None
        pdf_url = self.baseUrl + xpath_query[0]

        # Example PDF-name: "KW_44_Herbst_4_Mensa_2018.pdf" or "KW_50_Winter_1_Mensa_-2018.pdf"
        pdf_name = pdf_url.split("/")[-1]
        wn_year_match = re.search(r"KW_([1-9]+\d*)_.*_-?(\d+).*", pdf_name, re.IGNORECASE)
        if not wn_year_match:
            raise RuntimeError(f"year-week-parsing failed for PDF {pdf_name}")
        week_number: int = int(wn_year_match.group(1))

        year_2d: int = int(wn_year_match.group(2))
        # convert 2-digit year into 4-digit year
        if len(str(year_2d)) not in [2, 4]:
            raise RuntimeError(f"year-parsing failed for PDF {pdf_name}. parsed-year={year_2d}")
        if len(str(year_2d)) == 2:
            year: int = 2000 + year_2d
        else:
            year = year_2d

        with tempfile.NamedTemporaryFile() as temp_pdf:
            # download pdf
            response = requests.get(pdf_url, timeout=10.0)
            temp_pdf.write(response.content)
            with tempfile.NamedTemporaryFile() as temp_txt:
                # convert pdf to text by calling pdftotext; only convert first page to txt (-l 1)
                call(
                    ["pdftotext", "-l", "1", "-layout", temp_pdf.name, temp_txt.name],
                )  # nosec: all input is fully defined
                with open(temp_txt.name, "r", encoding="utf-8") as myfile:
                    # read generated text file
                    data = myfile.read()
                    return self.get_menus(data, year, week_number)

    def get_menus(self, text: str, year: int, week_number: int) -> Optional[Dict[datetime.date, Menu]]:
        lines = text.splitlines()

        # get dish types
        # its the line before the first "***..." line
        dish_types_line = ""
        last_non_empty_line = -1
        for i, line in enumerate(lines):
            if "***" in line:
                if last_non_empty_line >= 0:
                    dish_types_line = lines[last_non_empty_line]
                break
            if line:
                last_non_empty_line = i
        dish_types = re.split(r"\s{2,}", dish_types_line)
        dish_types = [dt for dt in dish_types if dt]

        count = 0
        # get all dish lines
        for line in lines:
            if "Montag" in line:
                break
            count += 1  # noqa: SIM113
        lines = lines[count:]

        # get rid of Zusatzstoffe and Allergene: everything below the last ***-delimiter is irrelevant
        last_relevant_line = len(lines)
        for index, line in enumerate(lines):
            if "***" in line:
                last_relevant_line = index
        lines = lines[:last_relevant_line]

        days_list = [
            d
            for d in re.split(
                r"(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag),\s\d{1,2}.\d{1,2}.\d{4}",
                "\n".join(lines).replace("*", "").strip(),
            )
            if d not in ["", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        ]
        if len(days_list) != 7:
            # as the Mediziner Mensa is part of hospital, it should serve food on each day
            return None
        days = {
            "mon": days_list[0],
            "tue": days_list[1],
            "wed": days_list[2],
            "thu": days_list[3],
            "fri": days_list[4],
            "sat": days_list[5],
            "sun": days_list[6],
        }

        menus = {}
        for key in days:
            day_lines = unicodedata.normalize("NFKC", days[key]).splitlines(True)
            soup_str = ""
            mains_str = ""
            for day_line in day_lines:
                soup_str += day_line[:36].strip() + "\n"
                mains_str += day_line[40:100].strip() + "\n"

            soup_str = soup_str.replace("-\n", "").strip().replace("\n", " ")
            soup = self.parse_dish(soup_str)
            if len(dish_types) > 0:
                soup.dish_type = dish_types[0]
            else:
                soup.dish_type = "Suppe"
            dishes = []
            if soup.name not in ["", "Feiertag"]:
                dishes.append(soup)
            # https://regex101.com/r/MDFu1Z/1

            # prepare dish type
            dish_type = ""
            if len(dish_types) > 1:
                dish_type = dish_types[1]

            for dish_str in re.split(r"(\n{2,}|(?<!mit)\n(?=[A-Z]))", mains_str):
                if "Extraessen" in dish_str:
                    # now only "Extraessen" will follow
                    dish_type = "Extraessen"
                    continue
                dish_str = dish_str.strip().replace("\n", " ")
                dish = self.parse_dish(dish_str)
                dish.name = dish.name.strip()
                if dish.name not in ["", "Feiertag"]:
                    if dish_type:
                        dish.dish_type = dish_type
                    dishes.append(dish)

            date = self.get_date(year, week_number, self.weekday_positions[key])
            menu = Menu(date, dishes)
            # remove duplicates
            menu.remove_duplicates()
            menus[date] = menu

        return menus


class StraubingMensaMenuParser(MenuParser):
    url = "https://www.stwno.de/infomax/daten-extern/csv/HS-SR/{calendar_week}.csv"
    canteens = {Canteen.MENSA_STRAUBING}

    _label_subclasses: Dict[str, Set[Label]] = {
        "1": {Label.DYESTUFF},
        "2": {Label.PRESERVATIVES},
        "3": {Label.ANTIOXIDANTS},
        "4": {Label.FLAVOR_ENHANCER},
        "5": {Label.SULPHURS},
        "6": {Label.DYESTUFF},
        "7": {Label.WAXED},
        "8": {Label.PHOSPATES},
        "9": {Label.SWEETENERS},
        "10": {Label.PHENYLALANINE},
        "16": {Label.SULFITES},
        "17": {Label.PHENYLALANINE},
        "AA": {Label.WHEAT},
        "AB": {Label.RYE},
        "AC": {Label.BARLEY},
        "AD": {Label.OAT},
        "AE": {Label.SPELT},
        "AF": {Label.GLUTEN},
        "B": {Label.SHELLFISH},
        "C": {Label.CHICKEN_EGGS},
        "D": {Label.FISH},
        "E": {Label.PEANUTS},
        "F": {Label.SOY},
        "G": {Label.MILK},
        "HA": {Label.ALMONDS},
        "HB": {Label.HAZELNUTS},
        "HC": {Label.WALNUTS},
        "HD": {Label.CASHEWS},
        "HE": {Label.PECAN},
        "HG": {Label.PISTACHIOES},
        "HH": {Label.MACADAMIA},
        "I": {Label.CELERY},
        "J": {Label.MUSTARD},
        "K": {Label.SESAME},
        "L": {Label.SULPHURS, Label.SULFITES},
        "M": {Label.LUPIN},
        "N": {Label.MOLLUSCS},
    }

    def parse(self, canteen: Canteen) -> Optional[Dict[datetime.date, Menu]]:
        menus: Dict[datetime.date, Menu] = {}

        today = datetime.date.today()
        _, calendar_week, _ = today.isocalendar()

        # As we don't know how many weeks we can fetch,
        # repeat until there are non-valid dates in the downloaded csv file
        while True:
            page = requests.get(self.url.format(calendar_week=calendar_week), timeout=10.0)
            if page.ok:
                decoded_content = page.content.decode("cp1252")
                rows = self.parse_csv(decoded_content)

                date = util.parse_date(rows[0][0])
                # abort loop, if date of fetched csv is more than one week ago
                # as we can't request the year, only week information is given
                # Downloaded csv therefore may contain data from previous years
                if date < (today - datetime.timedelta(days=7)):
                    break

                menus.update(self.parse_menu(rows))

            else:
                # also abort loop, when there can't be a menu fetched
                break

            calendar_week += 1

        return menus

    @staticmethod
    def parse_csv(csv_string: str) -> List[List[str]]:
        cr = csv.reader(csv_string.splitlines(), delimiter=";")
        content = list(cr)
        return content[1:]

    def parse_menu(self, rows: List[List[str]]) -> Dict[datetime.date, Menu]:
        menus = {}

        date = util.parse_date(rows[0][0])
        dishes: List[Dish] = []

        for row in rows:
            dish_date = util.parse_date(row[0])
            if date != dish_date:
                menus[date] = Menu(date, dishes)
                date = dish_date
                dishes = []

            dish = self.parse_dish(row)
            dishes.append(dish)

        menus[date] = Menu(date, dishes)
        return menus

    def parse_dish(self, data: List[str]) -> Dish:
        labels: List[Label] = []

        title = data[3]
        bracket = title.rfind("(")  # find bracket that encloses labels

        if bracket != -1:
            labels.extend(self._parse_label(title[bracket:].replace("(", "").replace(")", "")))
            title = title[:bracket].strip()

        # prices are given as string with , instead of . as separator
        prices = Prices(
            Price(float(data[6].replace(",", "."))),
            Price(float(data[7].replace(",", "."))),
            Price(float(data[8].replace(",", "."))),
        )
        dish_type = data[2]

        marks = data[4]
        labels.extend(self._marks_to_labels(marks))

        return Dish(title, prices, labels, dish_type)

    @classmethod
    def _marks_to_labels(cls, marks: str) -> List[Label]:
        mark_to_label = {
            "VG": [Label.VEGAN, Label.VEGETARIAN],
            "V": [Label.VEGETARIAN],
            "G": [Label.POULTRY],
            "S": [Label.PORK],
            "A": [Label.ALCOHOL],
            "F": [Label.FISH],
            "R": [Label.BEEF],
            "L": [Label.LAMB],
            "W": [Label.WILD_MEAT],
        }

        labels = []
        for mark in marks.split(","):
            labels.extend(mark_to_label.get(mark, []))

        return labels


class MensaBildungscampusHeilbronnParser(MenuParser):
    base_url = "https://openmensa.org/api/v2/canteens/277"
    canteens = {Canteen.MENSA_BILDUNGSCAMPUS_HEILBRONN}

    def parse(self, canteen: Canteen) -> Optional[Dict[datetime.date, Menu]]:
        menus = {}

        def mutate(element):
            return Dish(
                element["name"],
                Prices(
                    Price(0, element["prices"]["students"], "Portion"),
                    Price(0, element["prices"]["employees"], "Portion"),
                    Price(0, element["prices"]["others"], "Portion"),
                ),
                set(),
                element["category"],
            )

        for date in self.__get_available_dates():
            dateobj: datetime.date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            page_link: str = self.base_url + "/days/" + date + "/meals"
            page: requests.Response = requests.get(page_link, timeout=10.0)
            if page.ok:
                dishes: List = list(map(mutate, page.json()))
                menus[dateobj] = Menu(dateobj, dishes)
        return menus

    def __get_available_dates(self):
        days: List = requests.get(self.base_url + "/days", timeout=10.0).json()

        # Weed out the closed days
        def predicate(element):
            return not element["closed"]

        def mutate(element):
            return element["date"]

        return list(map(mutate, filter(predicate, days)))
