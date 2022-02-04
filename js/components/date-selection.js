import {copyDate, dateFromString, dateToString} from "../modules/date-utils.js";
import m from "../external/mithril.module.js";
import {getHref} from "../modules/url-utils.js";
import translate from "../modules/translation.js";
import Tooltip from "./tooltip.js";


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
                    m(Tooltip, {tooltip: before ? translate("date", {date: before}) : translate("no-further-menu")},
                        m(m.route.Link, {href: getHref({mensa, date: before ? dateToString(before) : false}), class: "button", disabled: !before},
                            m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-angle-left"})))
                    ),
                ),
                m("p", {class: "control is-expanded"},
                    m("input", {
                        type: "date", class: "input", value: dateToString(currentDate), onchange: function (e) {
                            m.route.set(getHref({date: e.target.value}));
                        }
                    })
                ),
                m("p", {class: "control"},
                    m(Tooltip, {tooltip: after ? translate("date", {date: after}) : translate("no-further-menu"), class: "set-right"},
                        m(m.route.Link, {href: getHref({mensa, date: after ? dateToString(after) : false}), class: "button", disabled: !after},
                            m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-angle-right"})))
                    ),
                ),
            ]);
        }
    };
}
