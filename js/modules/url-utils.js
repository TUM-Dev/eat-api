import m from "../external/mithril.module.js";
import {dateFromString} from "./date-utils.js";

/**
 * Get a link, with respect to the given parameters
 *
 * @param {Object} parameters
 * @param {string} parameters.mensa
 * @param {string} date
 * @param {string} language
 * @param {string[]} filter
 * @returns {string}
 */
export function getHref({mensa, date, language, filter}) {
    if (language === undefined) {
        language = m.route.param("language");
    }

    if (mensa === undefined) {
        mensa = m.route.param("mensa");
    }

    if (date === undefined && m.route.param("date")) {
        date = m.route.param("date");
    }

    if (filter === undefined) {
        filter = getFilterLabels();
    }

    const parts = [language, mensa, date];

    let query = "";
    if (filter.length > 0) {
        const params = m.buildQueryString({filter});
        query = `?${params}`;
    }

    return `/${parts.filter(p => p).join("/")}${query}`;
}

/**
 * Get the date from the url
 *
 * @returns {Date}
 */
export function getUrlDate() {
    return dateFromString(m.route.param("date"));
}

/**
 * Get the filters, which should be filtered currently
 *
 * @returns {string[]}
 */
export function getFilterLabels() {
    const filters = m.route.param("filter");
    if (filters === undefined) {
        return [];
    }
    return filters;
}
