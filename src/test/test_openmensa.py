from datetime import date
from unittest import TestCase

from pyopenmensa.feed import LazyBuilder

from src import openmensa
from src.entities import Dish, DishType, Label, Menu, Price, Prices, Week


class OpenMensaTest(TestCase):
    def test_should_add_dish_to_canteen(self):
        canteen = LazyBuilder()
        dateobj = date(2017, 3, 27)
        dish = Dish(
            "Gulasch vom Schwein",
            Prices(Price(1.9)),
            {Label.PORK, Label.GLUTEN, Label.BARLEY, Label.WHEAT, Label.GARLIC, Label.MILK},
            DishType.DAILY_DISH,
        )

        openmensa.addDishToCanteen(dish, dateobj, canteen)
        meal = canteen._days[dateobj]["Speiseplan"][0]  # pylint: disable=protected-access
        self.assertEqual(meal[0], "Gulasch vom Schwein")
        self.assertEqual(meal[2], {"other": 190})

    def test_should_add_week_to_canteen(self):
        date_mon2 = date(2017, 11, 6)
        date_tue2 = date(2017, 11, 7)
        date_wed2 = date(2017, 11, 8)
        date_thu2 = date(2017, 11, 9)
        date_fri2 = date(2017, 11, 10)
        dish_aktion2 = Dish(
            "Pochiertes Lachsfilet mit Dillsoße dazu Minze-Reis",
            Prices(Price(6.5)),
            {Label.CELERY, Label.MILK},
            DishType.DAILY_DISH,
        )
        dish1_mon2 = Dish("Dampfkartoffeln mit Zucchinigemüse", Prices(Price(3.6)), {Label.CELERY}, DishType.DAILY_DISH)
        dish2_mon2 = Dish(
            "Valess-Schnitzel mit Tomaten-Couscous",
            Prices(Price(4.3)),
            {Label.CELERY, Label.GLUTEN, Label.CHICKEN_EGGS, Label.MILK},
            DishType.DAILY_DISH,
        )
        dish3_mon2 = Dish(
            "Kasslerpfanne mit frischen Champignons und Spätzle",
            Prices(Price(4.9)),
            {Label.CELERY, Label.MILK},
            DishType.DAILY_DISH,
        )
        dish1_tue2 = Dish(
            "Gemüsereispfanne mit geräuchertem Tofu",
            Prices(Price(3.6)),
            {Label.CELERY},
            DishType.DAILY_DISH,
        )
        dish2_tue2 = Dish(
            "Schweineschnitzel in Karottenpanade mit Rosmarin- Risoleekartoffeln",
            Prices(Price(5.3)),
            {Label.CELERY, Label.GLUTEN, Label.CHICKEN_EGGS},
            DishType.DAILY_DISH,
        )
        dish1_wed2 = Dish(
            "Spaghetti al Pomodoro",
            Prices(Price(3.6)),
            {Label.CELERY, Label.GLUTEN},
            DishType.DAILY_DISH,
        )
        dish2_wed2 = Dish(
            "Krustenbraten vom Schwein mit Kartoffelknödel und Krautsalat",
            Prices(Price(5.3)),
            {Label.CELERY, Label.GLUTEN},
            DishType.DAILY_DISH,
        )
        dish1_thu2 = Dish(
            "Red-Thaicurrysuppe mit Gemüse und Kokosmilch",
            Prices(Price(2.9)),
            {Label.CELERY},
            DishType.DAILY_DISH,
        )
        dish2_thu2 = Dish(
            "Senf-Eier mit Salzkartoffeln",
            Prices(Price(3.8)),
            {Label.CELERY, Label.MUSTARD, Label.MILK},
            DishType.DAILY_DISH,
        )
        dish3_thu2 = Dish(
            "Putengyros mit Zaziki und Tomatenreis",
            Prices(Price(5.3)),
            {Label.CELERY, Label.MILK},
            DishType.DAILY_DISH,
        )
        dish1_fri2 = Dish("Spiralnudeln mit Ratatouillegemüse", Prices(Price(3.6)), {Label.GLUTEN}, DishType.DAILY_DISH)
        dish2_fri2 = Dish("Milchreis mit warmen Sauerkirschen", Prices(Price(3)), {Label.MILK}, DishType.DAILY_DISH)
        dish3_fri2 = Dish(
            "Lasagne aus Seelachs und Blattspinat",
            Prices(Price(5.3)),
            {Label.CELERY, Label.GLUTEN, Label.MILK},
            DishType.DAILY_DISH,
        )
        menu_mon2 = Menu(date_mon2, [dish_aktion2, dish1_mon2, dish2_mon2, dish3_mon2])
        menu_tue2 = Menu(date_tue2, [dish_aktion2, dish1_tue2, dish2_tue2])
        menu_wed2 = Menu(date_wed2, [dish_aktion2, dish1_wed2, dish2_wed2])
        menu_thu2 = Menu(date_thu2, [dish_aktion2, dish1_thu2, dish2_thu2, dish3_thu2])
        menu_fri2 = Menu(date_fri2, [dish_aktion2, dish1_fri2, dish2_fri2, dish3_fri2])
        week = {
            date_mon2: menu_mon2,
            date_tue2: menu_tue2,
            date_wed2: menu_wed2,
            date_thu2: menu_thu2,
            date_fri2: menu_fri2,
        }
        weeks = Week.to_weeks(week)

        canteen = openmensa.weeksToCanteenFeed(weeks)
        self.assertEqual(canteen.hasMealsFor(date_mon2), True)
        self.assertEqual(canteen.hasMealsFor(date_tue2), True)
        self.assertEqual(canteen.hasMealsFor(date_wed2), True)
        self.assertEqual(canteen.hasMealsFor(date_thu2), True)
        self.assertEqual(canteen.hasMealsFor(date_fri2), True)

        canteen_wed2 = canteen._days[date_wed2]["Speiseplan"]  # pylint: disable=protected-access
        self.assertEqual(canteen_wed2[0], ("Pochiertes Lachsfilet mit Dillsoße dazu Minze-Reis", [], {"other": 650}))
        self.assertEqual(canteen_wed2[1], ("Spaghetti al Pomodoro", [], {"other": 360}))
        self.assertEqual(
            canteen_wed2[2],
            ("Krustenbraten vom Schwein mit Kartoffelknödel und Krautsalat", [], {"other": 530}),
        )
