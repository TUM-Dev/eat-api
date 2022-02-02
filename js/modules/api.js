import m from "../external/mithril.module.js";

import {padNumber} from "./date-utils.js";

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

export function getCanteens(){
    return m.request({
        method: "GET",
        url: "enums/canteens.json"
    });
}

export function getLabels(){
    return m.request({
        method: "GET",
        url: "enums/labels.json"
    });
}
