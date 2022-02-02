import m from "../external/mithril.module.js";
import {modal as Labels, subline, getFilteredDishes} from "./labels.js";
import {getWeek} from "../modules/date-utils.js";
import translate, {getLanguage} from "../modules/translation.js";
import Tooltip from "./tooltip.js";
import {getUrlDate} from "../modules/url-utils.js";
import {getMenuForDate} from "../modules/api.js";

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
            if (vnode.attrs.items === 0) {
                return;
            }

            const content = [m("tr", {class: "has-background-light is-clickable", onclick},
                m("td", {colspan: 2, class: "has-text-centered"},
                    m("button", {class: "button is-light"}, `${extended ? "Hide" : "Show"} filtered dishes (${vnode.attrs.items})`)
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
        currentParams: "",
        menu: null,
        loading: true,
        error: "",
        fetch: function () {
            const mensa = m.route.param("mensa");
            const currentDate = getUrlDate();
            const languageObject = getLanguage();

            const params = {mensa, currentDate, languageObject};
            // additional param check, as this may be requested multiple times, through mithril
            const paramsJson = JSON.stringify(params);
            if (this.currentParams === paramsJson) {
                return;
            }
            this.currentParams = paramsJson;

            MenuData.loading = true;
            getMenuForDate(params)
                .then(function (menu) {
                    MenuData.error = "";
                    MenuData.menu = menu;
                    MenuData.loading = false;
                })
                .catch(function () {
                    MenuData.error = translate("no-menu-for-week", {week: getWeek(currentDate).week, canteen: m.route.param("mensa")});
                    MenuData.loading = false;
                });
        }
    };

    return {
        oninit: MenuData.fetch,
        onupdate: MenuData.fetch,
        view: function () {
            if (MenuData.error) {
                return m("div", MenuData.error);
            } else if (MenuData.loading) {
                return m("div", translate("loading"));
            }

            const menuOfTheDay = MenuData.menu;
            if (!menuOfTheDay) {
                return m("div", translate("no-menu-for-date", {date: getUrlDate()}));
            } else {
                const {show: dishes, hide: additional} = getFilteredDishes(menuOfTheDay.dishes);

                return m("div", {class: "mt-3"},
                    m("table", {class: "table is-hoverable is-fullwidth"}, [
                        m("thead", m("tr", [
                            m("th", m("span", [
                                translate("dish"),
                                m(Labels, m("span", {class: "icon icon-small"},
                                    m(Tooltip, {class: "is-inline-block has-text-weight-normal", tooltip: translate("info-labels")},
                                        m("i", {class: "fa fa-info-circle"}))))
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
