# -*- coding: utf-8 -*-

import json
import re
from typing import Dict, Optional, Sequence, Union, List, Any, Set
from datetime import datetime


class Price:
    
    base_price: Union[float, str]
    price_per_unit: Optional[float]
    unit: Optional[str]

    def __init__(self, base_price: Union[float, str], price_per_unit: Optional[float] = None, unit: Optional[str] = None):
        try:
            self.base_price = float(base_price)
        except ValueError:
            self.base_price = base_price
        self.price_per_unit = price_per_unit
        self.unit = unit

    def __repr__(self):
        if self.price_per_unit and self.unit:
            if isinstance(self.base_price, float):
                return "{:.2f}€ + {:.2f} {}".format(self.base_price, self.price_per_unit, self.unit)
            else:
                return "{} + {} {}".format(self.base_price, self.price_per_unit, self.unit)
        else:
            if isinstance(self.base_price, float):
                return "{:.2f}€".format(self.base_price)
            else:
                return "{}".format(self.base_price)

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return (self.base_price == other.base_price
                    and self.price_per_unit == other.price_per_unit
                    and self.unit == other.unit)
        return False

    def to_json_obj(self):
        return {"base_price": self.base_price, "price_per_unit": self.price_per_unit, "unit": self.unit}

    def __hash__(self):
        # http://stackoverflow.com/questions/4005318/how-to-implement-a-good-hash-function-in-python
        return (hash(self.base_price) << 1) ^ hash(self.price_per_unit) ^ hash(self.unit)


class Prices:
    students: Price
    staff: Price
    guests: Price

    def __init__(self, students: Optional[Price] = None, staff: Optional[Price] = None, guests: Optional[Price] = None):
        if students is None:
            self.students = Price("N/A")
        else:
            self.students = students
        # fall back to the students price if there is only one price available
        if staff is None:
            self.staff = self.students
        else:
            self.staff = staff
        if guests is None:
            self.guests = self.students
        else:
            self.guests = guests

    def setBasePrice(self, base_price: float):
        self.students.base_price = base_price
        self.staff.base_price = base_price
        self.guests.base_price = base_price

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return (self.students == other.students
                    and self.staff == other.staff
                    and self.guests == other.guests)
        return False

    def __repr__(self):
        return "students: {}, staff: {}, guests: {}".format(self.students, self.staff, self.guests)
        if self.price_per_unit and self.unit:
            if isinstance(self.base_price, float):
                return "{:.2f}€ + {:.2f} {}".format(self.base_price, self.price_per_unit, self.unit)
            else:
                return "{} + {} {}".format(self.base_price, self.price_per_unit, self.unit)
        else:
            if isinstance(self.base_price, float):
                return "{:.2f}€".format(self.base_price)
            else:
                return "{}".format(self.base_price)

    def to_json_obj(self):
        return {"students": self.students.to_json_obj(), "staff": self.staff.to_json_obj(), "guests": self.guests.to_json_obj()}
    
    def __hash__(self):
        # http://stackoverflow.com/questions/4005318/how-to-implement-a-good-hash-function-in-python
        return hash(self.students) ^ hash(self.staff) ^ hash(self.guests)


class Ingredients:

    location: str
    ingredient_set: Set[str]

    ingredient_lookup = {
        "GQB" : "Certified Quality - Bavaria",
        "MSC" : "Marine Stewardship Council",

        "1" : "with dyestuff",
        "2" : "with preservative",
        "3" : "with antioxidant",
        "4" : "with flavor enhancers",
        "5" : "sulphured",
        "6" : "blackened (olive)",
        "7" : "waxed",
        "8" : "with phosphate",
        "9" : "with sweeteners",
        "10" : "contains a source of phenylalanine",
        "11" : "with sugar and sweeteners",
        "13" : "with cocoa-containing grease",
        "14" : "with gelatin",
        "99" : "with alcohol",

        "f" : "meatless dish",
        "v" : "vegan dish",
        "S" : "with pork",
        "R" : "with beef",
        "K" : "with veal",
        "G" : "with poultry",  # mediziner mensa
        "W" : "with wild meat",  # mediziner mensa
        "L" : "with lamb",  # mediziner mensa
        "Kn" : "with garlic",
        "Ei" : "with chicken egg",
        "En" : "with peanut",
        "Fi" : "with fish",
        "Gl" : "with gluten-containing cereals",
        "GlW" : "with wheat",
        "GlR" : "with rye",
        "GlG" : "with barley",
        "GlH" : "with oats",
        "GlD" : "with spelt",
        "Kr" : "with crustaceans",
        "Lu" : "with lupines",
        "Mi" : "with milk and lactose",
        "Sc" : "with shell fruits",
        "ScM" : "with almonds",
        "ScH" : "with hazelnuts",
        "ScW" : "with Walnuts",
        "ScC" : "with cashew nuts",
        "ScP" : "with pistachios",
        "Se" : "with sesame seeds",
        "Sf" : "with mustard",
        "Sl" : "with celery",
        "So" : "with soy",
        "Sw" : "with sulfur dioxide and sulfites",
        "Wt" : "with mollusks",
    }
    """A dictionary of all ingredients (from the Studentenwerk) with their description."""

    fmi_ingredient_lookup = {
        "Gluten" : "Gl",
        "Laktose" : "Mi",
        "Milcheiweiß" : "Mi",
        "Milch" : "Mi",
        "Ei" : "Ei",
        "Hühnerei" : "Ei",
        "Soja" : "So",
        "Nüsse" : "Sc",
        "Erdnuss" : "En",
        "Sellerie" : "Sl",
        "Fisch" : "Si",
        "Krebstiere" : "Kr",
        "Weichtiere" : "Wt",
        "Sesam" : "Se",
        "Senf" : "Sf",
    }

    mediziner_ingredient_lookup = {
        "1" : "1",
        "2" : "2",
        "3" : "3",
        "4" : "4",
        "5" : "5",
        "6" : "6",
        "7" : "7",
        "8" : "8",
        "9" : "9",

        "A" : "99",
        "B" : "Gl",
        "C" : "Kr",
        "E" : "Fi",
        "F" : "Fi",
        "G" : "G",
        "H" : "En",
        "K" : "K",
        "L" : "L",
        "M" : "So",
        "N" : "Mi",
        "O" : "Sc",
        "P" : "Sl",
        "R" : "R",
        "S" : "S",
        "T" : "Sf",
        "U" : "Se",
        "V" : "Sw",
        "W" : "W",
        "X" : "Lu",
        "Y" : "Ei",
        "Z" : "Wt",
    }

    def __init__(self, location: str):
        self.location = location
        self.ingredient_set = set()

    def _values_lookup(self, values: Sequence[str], lookup: Optional[Dict[str, str]]):
        """
        Normalizes ingredients to the self.ingredient_lookup codes.

        Args:
            values: A sequence of ingredients codes.
            lookup: If needed, a mapping from a canteen specific ingredients codes to the self.ingredient_lookup codes.
        """
        for value in values:
            # ignore empty values
            if not value or value.isspace():
                continue
            if (not lookup and value not in self.ingredient_lookup) or (lookup and value not in lookup):

                # sometimes the ‘,’ is missing between the ingredients (especially with IPP) and we try to split again
                # with capital letters.
                split_values: List[Any] = re.findall(r'[a-züöäA-ZÜÖÄ][^A-ZÜÖÄ]*', value)
                if split_values:
                    self._values_lookup(split_values, lookup)
                    continue
                else:
                    print("Unknown ingredient for " + self.location + " found: " + str(value))
                    continue

            if lookup:
                self.ingredient_set.add(lookup[value])
            else:
                self.ingredient_set.add(value)

    def parse_ingredients(self, values: str):
        """
        Parse and creates a normalized list of ingredients.

        Args:
            values: String with comma separated ingredients codes.
        """
        values = values.strip()
        split_values: List[str] = values.split(',')
        # check for special parser/ingredient translation required
        if self.location == "fmi-bistro":
            self._values_lookup(split_values, self.fmi_ingredient_lookup)
        elif self.location == "mediziner-mensa":
            self._values_lookup(split_values, self.mediziner_ingredient_lookup)
        # default to the "Studentenwerk" ingredients
        # "ipp-bistro" also uses the "Studentenwerk" ingredients since all
        # dishes contain the same ingredients
        else:
            self._values_lookup(split_values, self.ingredient_lookup)

    def __hash__(self):
        return hash(frozenset(self.ingredient_set))


class Dish:
    name: str
    prices: Prices
    ingredients: Ingredients
    dish_type: str

    def __init__(self, name: str, prices: Prices, ingredients: Ingredients, dish_type: str):
        self.name = name
        self.prices = prices
        self.ingredients = ingredients
        self.dish_type = dish_type

    def __repr__(self):
        return "%s %s: %s" % (self.name, str(sorted(self.ingredients)), str(self.prices))

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return (self.name == other.name
                    and self.prices == other.prices
                    and self.ingredients == other.ingredients
                    and self.dish_type == other.dish_type)
        return False

    def to_json_obj(self):
        return {"name": self.name, "prices": self.prices.to_json_obj(),
             "ingredients": sorted(self.ingredients), "dish_type": self.dish_type}

    def __hash__(self):
        # http://stackoverflow.com/questions/4005318/how-to-implement-a-good-hash-function-in-python
        return (hash(self.name) << 1) ^ hash(self.prices) ^ hash(frozenset(self.ingredients)) ^ hash(self.dish_type)


class Menu:
    menu_date: datetime
    dishes: List[Dish]

    def __init__(self, menu_date: datetime, dishes: List[Dish]):
        self.menu_date = menu_date
        self.dishes = dishes

    def __repr__(self):
        menu_str = str(self.menu_date) + ": " + str(self.dishes)
        return menu_str

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            dishes_equal = set(self.dishes) == set(other.dishes)
            date_equal = self.menu_date == other.menu_date
            return dishes_equal and date_equal
        return False

    def remove_duplicates(self):
        unique: List[Dish] = list()
        seen: Set[Dish] = set()

        for d in self.dishes:
            if d not in seen:
                unique.append(d)
                seen.add(d)

        self.dishes = unique


class Week:

    calendar_week: int
    year: int
    days: int

    def __init__(self, calendar_week: int, year: int, days: int):
        self.calendar_week = calendar_week
        self.year = year
        self.days = days

    def __repr__(self):
        week_str = "Week %s-%s" % (self.year, self.calendar_week)
        for day in self.days:
            week_str += "\n %s" % day
        return week_str

    def to_json_obj(self):
        return {"number": self.calendar_week, "year": self.year,
             "days": [{"date": str(menu.menu_date), "dishes": [dish.to_json_obj() for dish in menu.dishes]} for menu in
                      self.days]}

    def to_json(self):
        week_json: str = json.dumps(
            self.to_json_obj(),
            ensure_ascii=False, indent=4)
        return week_json

    @staticmethod
    def to_weeks(menus):
        weeks: Dict[int, Week] = {}
        for menu_key in menus:
            menu: Menu = menus[menu_key]
            menu_date = menu.menu_date
            # get calendar week
            calendar_week = menu_date.isocalendar()[1]
            # get year of the calendar week. watch out that for instance jan 01 can still be in week 52 of the
            # previous year
            year_of_calendar_week = menu_date.year - 1 \
                if calendar_week == 52 and menu_date.month == 1 else menu_date.year

            # append menus to respective week
            week: Week = weeks.get(calendar_week, Week(calendar_week, year_of_calendar_week, []))
            week.days.append(menu)
            weeks[calendar_week] = week
        return weeks
