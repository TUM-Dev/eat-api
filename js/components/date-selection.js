import {copyDate, dateToString} from "../modules/date-utils.js";
import m from "../external/mithril.module.js";
import {getHref, getUrlDate} from "../modules/url-utils.js";
import translate from "../modules/translation.js";
import Tooltip from "./tooltip.js";
import {getNextAvailableDate} from "../modules/api.js";
import {getLanguage} from "../modules/translation.js";


export default function DateSelection() {
    let before, after, search;
    return {
        onupdate: function () {
            if (search?.valueOf() === getUrlDate().valueOf()) {
                return;
            }
            search = getUrlDate();
            after = false;
            before = false;

            const mensa = m.route.param("mensa");
            const languageObject = getLanguage();

            const startAfter = copyDate(search);
            startAfter.setDate(startAfter.getDate() + 1);
            getNextAvailableDate({starting: startAfter, mensa, languageObject})
                .then(d => after = d)
                .catch(() => after = false);

            const startBefore = copyDate(search);
            startBefore.setDate(startBefore.getDate() - 1);
            getNextAvailableDate({starting: startBefore, mensa, languageObject, step: -1})
                .then(d => before = d)
                .catch(() => before = false);
        },
        view: function () {
            const currentDate = getUrlDate();
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
