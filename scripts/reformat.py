#!/bin/python3
import json
import os
import re
from datetime import datetime
from datetime import timedelta


class Dish:
    def __init__(self, name, prices, ingredients, dish_type, date):
        self.name = name
        self.prices = prices
        self.ingredients = ingredients
        self.dish_type = self.uniformDishType(dish_type)
        self.date = date

    @staticmethod
    def uniformDishType(dish_type):
        if not dish_type or dish_type == "":
            return "Tagesgericht"
        return re.sub(r"\s*\d+$", "", dish_type)


class Canteen:
    def __init__(self, node):
        self.canteen_id = node.get("canteen_id")
        self.dishes = []
        # Get the reference date (yesterday)
        refDate = datetime.today() - timedelta(days=1)
        for week in node.get("weeks"):
            for day in week.get("days"):
                date = day.get("date")
                if date:
                    date_parsed = datetime.strptime(date, "%Y-%m-%d")
                    # Only add dishes, their date is greater than yesterday
                    if date_parsed >= refDate:
                        for dish in day.get("dishes"):
                            self.dishes.append(
                                Dish(
                                    dish.get("name"),
                                    dish.get("prices"),
                                    dish.get("ingredients", ""),
                                    dish.get("dish_type"),
                                    date,
                                ),
                            )


def main():
    if os.path.isdir("dist"):
        os.chdir("dist")

        canteens = []
        print('Loading "all.json"')
        # Read all menus from the "all.json" file
        if os.path.isfile("all.json"):
            with open("all.json", "r") as input_file:
                data = json.load(input_file)
                print('Parsing "all.json"')
                for c in data.get("canteens"):
                    canteens.append(Canteen(c))

        print('Saving result to "all_ref.json"')
        with open("all_ref.json", "w") as outfile:
            json.dump(canteens, outfile, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
        print("Done")


if __name__ == "__main__":
    main()
