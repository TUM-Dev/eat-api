import m from "../external/mithril.module.js";

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
