import m from "../external/mithril.module.js";

import {copyDate, dateFromString, getWeek, padNumber} from "./date-utils.js";

const cacheMenu = {};

/**
 * Return the menu from the api, result can be cached
 *
 * @param {string} mensa
 * @param {number} year
 * @param {(number|string)} week
 * @param {Object} languageObject
 * @returns {Promise<*>}
 */
export async function getMenu({mensa, year, week, languageObject}) {
    const params = {
        mensa,
        year,
        week: padNumber(week),
        language: languageObject["name"],
    };
    const stringParams = JSON.stringify(params);

    // if parameters have not changed, no new request is required
    if (stringParams in cacheMenu) {
        return cacheMenu[stringParams];
    }

    // include language for the check, whether parameters have changed
    delete params.language; // delete language, before it is used for the request

    cacheMenu[stringParams] = m.request({
        method: "GET",
        url: `${languageObject["base_url"]}:mensa/:year/:week.json`,
        params
    });
    return cacheMenu[stringParams];
}

/**
 * Return the menu for a single date
 *
 * @param {Date} currentDate
 * @param {string} mensa
 * @param {Object} languageObject
 * @returns {Promise<*>}
 */
export async function getMenuForDate({currentDate, mensa, languageObject}) {
    function selectedDay(day) {
        return currentDate.valueOf() === dateFromString(day.date).valueOf();
    }

    const {week, year} = getWeek(currentDate);
    const menu = await getMenu({mensa, week, year, languageObject});
    return menu.days.find(selectedDay);
}

/**
 * Get a date, with an available menu
 *
 * @param {Date} starting
 * @param {string} mensa
 * @param {Object} languageObject
 * @param {number} maxOffset maximum number of tries, avoids endless loop
 * @param {number} step can be used, to search backwards
 * @returns {Promise<Date>}
 */
export async function getNextAvailableDate({starting, mensa, languageObject, maxOffset = 20, step = 1}) {
    const tryDate = copyDate(starting);
    for (let i = 0; i < maxOffset; i++) {
        try {
            const tryMenu = await getMenuForDate({currentDate: tryDate, mensa, languageObject});
            if (tryMenu) {
                return tryDate;
            }
        } catch (e) { // eslint-disable-line no-empty
        }
        tryDate.setDate(tryDate.getDate() + step);
    }
    throw new Error("no date found within maxOffset and step");
}

export function getCanteens() {
    return m.request({
        method: "GET",
        url: "enums/canteens.json"
    });
}

export function getLabels() {
    return m.request({
        method: "GET",
        url: "enums/labels.json"
    });
}
