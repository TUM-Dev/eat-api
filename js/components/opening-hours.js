import m from "../external/mithril.module.js";
import translate from "../modules/translation.js";

import {canteens} from "./location-selection.js";
import { dateFromString, getDateWithTime} from "../modules/date-utils.js";


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

export default function OpeningHours() {
    return {
        view: function () {
            const openingHours = getOpeningHours(m.route.param("mensa"));
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
                m("span", {class: textColor}, translate("opened", openingHoursDate))
            );
        }
    };
}
