# -*- coding: utf-8 -*-

import csv
import datetime
import re
import tempfile
import unicodedata
from abc import ABC, abstractmethod
from enum import Enum, auto
from subprocess import call  # noqa: S404 all the inputs is fully defined
from typing import Dict, List, Optional, Set, Tuple
from warnings import warn

import requests  # type: ignore
from lxml import html

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
        PIZZA_VEGGIE = (4.5, 5.0, 6.0)
        PIZZA_MEAT = (5.0, 5.5, 6.5)

        def __init__(self, p1, p2, p3):
            self.price = (p1, p2, p3)

    # meat and vegetarian base prices for Students, Staff, Guests
    class SelfServicePricePerUnitType(Enum):
        CLASSIC = 0.90, 1.15, 1.60
        SOUP_STEW = 0.33, 1.15, 1.60
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
        "8": {Label.PHOSPHATES},
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
        "ScP": {Label.PISTACHIOS},
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
        "StudiTopf": Prices(Price(1.00), Price(2.90), Price(3.90)),
        "Gericht 1": Prices(Price(2.95), Price(3.90), Price(5.10)),
        "Gericht 2": Prices(Price(3.35), Price(4.60), Price(5.90)),
        "Gericht 3": Prices(Price(3.65), Price(4.95), Price(6.30)),
        "Gericht 4": Prices(Price(4.15), Price(5.30), Price(6.70)),
        "Gericht 5": Prices(Price(4.65), Price(5.65), Price(7.10)),
        "Gericht 6": Prices(Price(5.25), Price(6.25), Price(7.80)),
        "Beilage 1": Prices(Price(0.80), Price(1.05), Price(1.50)),
        "Brot": Prices(Price(0.80), Price(1.05), Price(1.50)),
        "Obst": Prices(Price(0.80), Price(1.05), Price(1.50)),
        "Beilage 2": Prices(Price(0.90), Price(1.25), Price(1.70)),
        "Beilage 3": Prices(Price(1.10), Price(1.45), Price(2.00)),
        "Beilage 4": Prices(Price(1.60), Price(1.80), Price(2.60)),
        "Pizza - Veggie": Prices(Price(4.50), Price(5.00), Price(6.00)),
        "Pizza - Wurst. Schinken. Fisch. Meeresfrüchte": Prices(Price(5.00), Price(5.50), Price(6.50)),
        "Salatbuffet": Prices(Price(0, 0.90, "100g"), Price(0, 1.15, "100g"), Price(0, 1.60, "100g")),
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
                base_price_type = StudentenwerkMenuParser.SelfServiceBasePriceType.PIZZA_VEGGIE
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
            except Exception as e:
                print(f"Exception while parsing menu. Skipping current date. Exception args: {e.args}")
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
        dish_markers_meatless: List[str] = menu_html.xpath(
            "//li[contains(@class, 'c-menu-dish-list__item  u-clearfix  "
            "clearfix  js-menu__list-item')]/@data-essen-fleischlos",
        )

        # create Dish objects with prices
        dishes: List[Dish] = []
        for dish_name, dish_type, additional_marker, allergen_marker, type_marker, meatless_marker in zip(
            dish_names,
            dish_types,
            dish_markers_additional,
            dish_markers_allergen,
            dish_markers_type,
            dish_markers_meatless,
        ):
            # parse labels
            labels = set()
            labels |= StudentenwerkMenuParser._parse_label(additional_marker)
            labels |= StudentenwerkMenuParser._parse_label(allergen_marker)
            labels |= StudentenwerkMenuParser._parse_label(type_marker)
            StudentenwerkMenuParser.__add_diet(labels, meatless_marker)
            # do not price side dishes
            prices: Prices
            if dish_type == "Beilagen":
                # set classic prices without any base price
                prices = StudentenwerkMenuParser.__get_self_service_prices(
                    StudentenwerkMenuParser.SelfServiceBasePriceType.VEGETARIAN_SOUP_STEW,
                    StudentenwerkMenuParser.SelfServicePricePerUnitType.CLASSIC,
                )
            else:
                # find prices
                values = (dish_type, additional_marker, allergen_marker, type_marker, meatless_marker)
                prices = StudentenwerkMenuParser.__get_price(canteen, values, dish_name)
            dishes.append(Dish(dish_name, prices, labels, dish_type))

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
        "hPi": {Label.PISTACHIOS},
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
                        call(["/usr/bin/pdftotext", "-layout", temp_pdf.name, temp_txt.name])  # noqa: S603 all input is fully defined
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
                line[estimated_column_end - delta : min(estimated_column_end + delta, len(line))],
            )[0]
        except IndexError:
            return None
        price = float(price_str.replace(",", "."))
        try:
            labels_str = re.findall(
                r"[A-Za-z](?:,[A-Za-z]+)*",
                line[max(estimated_column_begin - delta, 0) : estimated_column_begin + delta],
            )[0]
        except IndexError:
            labels_str = ""
        return labels_str, price


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
        "8": {Label.PHOSPHATES},
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
                call(["/usr/bin/pdftotext", "-l", "1", "-layout", temp_pdf.name, temp_txt.name])  # noqa: S603 all input is fully defined
                with open(temp_txt.name, "r", encoding="utf-8") as myfile:
                    # read generated text file
                    data = myfile.read()
                    return self.get_menus(data, year, week_number)

    def get_menus(self, text: str, year: int, week_number: int) -> Optional[Dict[datetime.date, Menu]]:
        lines = text.splitlines()

        # get dish types
        # it's the line before the first "***..." line
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
        for key, day in days.items():
            day_lines = unicodedata.normalize("NFKC", day).splitlines(True)
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

            # prepare dish type
            dish_type = ""
            if len(dish_types) > 1:
                dish_type = dish_types[1]

            # https://regex101.com/r/MDFu1Z/1
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
        "8": {Label.PHOSPHATES},
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
        "HG": {Label.PISTACHIOS},
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
        labels = set()

        title = data[3]
        bracket = title.rfind("(")  # find bracket that encloses labels

        if bracket != -1:
            labels.update(self._parse_label(title[bracket:].replace("(", "").replace(")", "")))
            title = title[:bracket].strip()

        # prices are given as string with , instead of . as separator
        prices = Prices(
            Price(float(data[6].replace(",", "."))),
            Price(float(data[7].replace(",", "."))),
            Price(float(data[8].replace(",", "."))),
        )
        dish_type = data[2]

        marks = data[4]
        labels.update(self._marks_to_labels(marks))

        return Dish(title, prices, labels, dish_type)

    @classmethod
    def _marks_to_labels(cls, marks: str) -> set[Label]:
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

        labels = set()
        for mark in marks.split(","):
            labels.update(mark_to_label.get(mark, []))

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
