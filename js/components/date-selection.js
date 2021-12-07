import {mithril as m} from "../external.js";

import {copyDate, dateFromString, dateToString} from "../modules/date-util.js";
import {getHref} from "../modules/url-util.js";

export default function DateSelection() {
    return {
        view: function () {
            const currentDate = dateFromString(m.route.param("date"));

            const before = copyDate(currentDate);
            before.setDate(before.getDate() - 1);
            const after = copyDate(currentDate);
            after.setDate(after.getDate() + 1);

            const mensa = m.route.param("mensa");

            return m("div", {class: "field has-addons"}, [
                m("p", {class: "control"},
                    m(m.route.Link, {href: getHref({mensa, date: dateToString(before)}), class: "button"},
                        m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-angle-left"}))),
                ),
                m("p", {class: "control"},
                    m("input", {
                        type: "date", class: "input", value: dateToString(currentDate), onchange: function (e) {
                            m.route.set(getHref({date: e.target.value}));
                        }
                    })
                ),
                m("p", {class: "control"},
                    m(m.route.Link, {href: getHref({mensa, date: dateToString(after)}), class: "button"},
                        m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-angle-right"})))
                ),
            ]);
        }
    };
}
