import m from "../external/mithril.module.js";
import {modal as Labels, subline, getFilteredDishes} from "./labels.js";
import {dateFromString, getWeek, padNumber} from "../modules/date-utils.js";
import translate, {getLanguage} from "../modules/translation.js";

function getPrice(prices, type) {
    if (Object.prototype.hasOwnProperty.call(prices, type)) {
        const price = prices[type];
        if (price != null) {
            let priceStr = null;

            // Base price:
            const basePrice = parseFloat(price.base_price);
            if (!isNaN(basePrice) && basePrice > 0.0) {
                priceStr = basePrice.toFixed(2) + "€";
            }

            // Unit per price:
            const pricePerUnit = parseFloat(price.price_per_unit);
            if (!isNaN(pricePerUnit) && pricePerUnit > 0.0 && price.unit != null) {
                if (priceStr) {
                    priceStr += " + ";
                } else {
                    priceStr = "";
                }
                priceStr += pricePerUnit.toFixed(2) + "€/" + price.unit;
            }
            return priceStr;
        }
    }
    return "";
}

function Dishes() {
    return {
        view: function (vnode) {
            return [vnode.attrs.dishes.map(function (dish) {
                return m("tr", [
                    m("td", [
                        m("p", dish.name),
                        m(Labels, {selectedLabels: dish.labels, readOnly: true},
                            m("span", {class: "is-size-7"}, subline(dish.labels))
                        )
                    ]),
                    m("td", getPrice(dish.prices, "students"))
                ]);
            })];
        }
    };
}

function ShowMore() {
    let extended = false;

    function onclick() {
        extended = !extended;
    }

    return {
        view: function (vnode) {
            // Don't show the button, when no more items available
            if (vnode.attrs.items === 0){
                return;
            }

            const content = [m("tr", {class: "has-background-light is-clickable", onclick},
                m("td", {colspan: 2, class: "has-text-centered"},
                    m("button", {class: "button is-light"}, `${extended ? "Hide": "Show"} filtered dishes (${vnode.attrs.items})`)
                )
            )];
            if (extended) {
                content.push(...vnode.children);
            }
            return content;
        }
    };
}

export default function Menu() {
    const MenuData = {
        currentParams: {},
        menu: null,
        error: "",
        fetch: function () {
            const languageObject = getLanguage();
            // can't load data, until language is available
            if (!languageObject) {
                return;
            }
            const language = languageObject["name"];

            const currentDate = dateFromString(m.route.param("date"));
            const {week, year} = getWeek(currentDate);
            const params = {
                mensa: m.route.param("mensa"),
                year,
                week: padNumber(week),
                language
            };

            // if parameters have not changed, no new request is required
            const isDifferent = Object.entries(params) // iterate over params, as these are always complete
                .reduce((prev, [key, value]) => prev || MenuData.currentParams[key] !== value
                    , false);
            if (!isDifferent) {
                return;
            }
            MenuData.currentParams = params;

            m.request({
                method: "GET",
                url: `${languageObject["base_url"]}/:mensa/:year/:week.json`,
                params
            })
                .then(function (menu) {
                    MenuData.error = "";
                    MenuData.menu = menu;
                })
                .catch(function () {
                    MenuData.error = translate("no-menu-for-week", {week: getWeek(currentDate).week, canteen: m.route.param("mensa")});
                });
        }
    };

    return {
        oninit: MenuData.fetch,
        onupdate: MenuData.fetch,
        view: function () {
            function selectedDay(day) {
                return dateFromString(m.route.param("date")).valueOf() === dateFromString(day.date).valueOf();
            }

            if (MenuData.error) {
                return m("div", MenuData.error);
            } else if (!MenuData.menu) {
                return m("div", translate("loading"));
            }

            const menuOfTheDay = MenuData.menu.days.find(selectedDay);
            if (!menuOfTheDay) {
                return m("div", translate("no-menu-for-date", {date: dateFromString(m.route.param("date"))}));
            } else {
                const {show: dishes, hide: additional} = getFilteredDishes(menuOfTheDay.dishes);

                return m("div",
                    m("table", {class: "table is-hoverable is-fullwidth"}, [
                        m("thead", m("tr", [
                            m("th", m("span", [
                                translate("dish"),
                                m(Labels, m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-info-circle"})))
                            ])),
                            m("th", translate("price"))
                        ])),
                        m("tbody", [
                            m(Dishes, {dishes}),
                            m(ShowMore, {items: additional.length}, m(Dishes, {dishes: additional}))
                        ]),
                        m("tfoot", m("tr", [m("td", {class: "p-0"}), m("td", {class: "p-0"})]))
                    ])
                );
            }
        }
    };
}
