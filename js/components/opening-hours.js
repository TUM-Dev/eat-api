import m from "../external/mithril.module.js";
import translate from "../modules/translation.js";

import {canteens} from "./location-selection.js";
import {dateFromString, getDateWithTime} from "../modules/date-utils.js";


function getOpeningHours(canteenId) {
    const canteen = canteens.find(v => v.canteen_id === canteenId);
    if (!canteen) {
        return false;
    }

    return canteen["open_hours"];
}

function getOpeningHoursForDate(openHours, date) {
    // mapping from js date weekdays to API weekdays
    const mapping = {
        0: "sun",
        1: "mon",
        2: "tue",
        3: "wed",
        4: "thu",
        5: "fri",
        6: "sat"
    };

    const weekDay = date.getDay();
    const apiWeekDay = mapping[weekDay];

    return openHours[apiWeekDay];
}

// 0 = not today, 1 = will open, 2 = open, 3 = was open
function getStatus(openingHoursDate, selectedDate) {
    // check if selectedDate is today
    const now = new Date();

    if (selectedDate.getDate() !== now.getDate() || selectedDate.getMonth() !== now.getMonth() || selectedDate.getFullYear() !== now.getFullYear()) {
        return 0;
    }

    const start = getDateWithTime(selectedDate, openingHoursDate["start"]);
    if (now < start) {
        return 1;
    }

    const end = getDateWithTime(selectedDate, openingHoursDate["end"]);
    if (now > end) {
        return 3;
    }
    return 2;
}

function modal() {
    let showModal = false;

    return {
        view: function (vnode) {
            let modalClass = "modal";
            if (showModal) {
                modalClass += " is-active";
            }

            const {canteen} = vnode.attrs;

            return m("span", [
                m("span", {class: "is-clickable", onclick: () => showModal = true}, vnode.children),
                m("div", {class: modalClass}, [
                    m("div", {class: "modal-background", onclick: () => showModal = false}),
                    m("div", {class: "modal-content"},
                        m("div", {class: "card"},
                            m("div", {class: "card-content"},
                                m("div", {class: "content"},
                                    [
                                        m("h3", translate("opening-hours", {canteen})),
                                        m("table", [
                                            m("thead", [m("th", translate("weekday")), m("th", translate("opens")), m("th", translate("closes"))]),
                                            m("tbody", Object.entries(vnode.attrs.openingHours).map(v =>
                                                m("tr", [m("td", translate(v[0])), m("td", v[1].start), m("td", v[1].end)])
                                            ))
                                        ])
                                    ]
                                )))),
                    m("button", {class: "modal-close is-large", "aria-label": "close", onclick: () => showModal = false})
                ])
            ]);
        }
    };
}

export default function OpeningHours() {
    return {
        view: function () {
            const canteen = m.route.param("mensa");
            const openingHours = getOpeningHours(canteen);
            const selectedDate = dateFromString(m.route.param("date"));
            const openingHoursDate = getOpeningHoursForDate(openingHours, selectedDate);

            // if no open hours found, don't show any text
            if (!openingHoursDate) {
                return m("div");
            }

            const status = getStatus(openingHoursDate, selectedDate);
            const statusToClassMapping = {
                0: "",
                1: "has-text-info",
                2: "has-text-success",
                3: "has-text-danger",
            };
            const textColor = statusToClassMapping[status];

            return m("div", {class: "has-text-centered"},
                m("span", {class: textColor}, translate("opened", openingHoursDate)),
                m(modal, {openingHours, canteen}, m("i", {class: "fa fa-info-circle ml-1"}))
            );
        }
    };
}
