import {mithril as m} from "../external.js";

export function getHref({mensa, date}) {
    if (mensa === undefined) {
        mensa = m.route.param("mensa");
    }

    if (date === undefined && m.route.param("date")) {
        date = m.route.param("date");
    }

    const parts = [mensa, date];
    return `/${parts.filter(p => p).join("/")}`;
}
