from pyopenmensa.feed import LazyBuilder


def openmensa(weeks, directory):
    canteen = weeksToCanteenFeed(weeks)

    writeFeedToFile(canteen, directory)


def weeksToCanteenFeed(weeks):
    canteen = LazyBuilder()  # canteen container
    # iterate through weeks
    for calendar_week in weeks:
        # get Week object
        week = weeks[calendar_week]
        # get year of calendar week
        days = week.days

        # iterate through days
        for menu in days:

            # iterate through dishes
            for dish in menu.dishes:
                addDishToCanteen(dish, menu.menu_date, canteen)

    return canteen


def addDishToCanteen(dish, date, canteen):
    if isinstance(dish.prices.students.base_price, float):
        prices = {"other": dish.prices.students.base_price}
    else:
        prices = {}
    canteen.addMeal(date, "Speiseplan", dish.name, prices=prices)


def writeFeedToFile(canteen, directory):
    with open(f"{str(directory)}/feed.xml", "w") as outfile:
        outfile.write(canteen.toXMLFeed())
