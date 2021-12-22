import m from "../external/mithril.module.js";

import {getHref} from "../modules/url-utils.js";
import {changeLanguage} from "../modules/translation.js";

const languages = [
    {
        "name": "DE",
        "base_url": "https://tum-dev.github.io/eat-api/",
        "label": "Deutsch",
        "flag": "\ud83c\udde9\ud83c\uddea"
    },
    {
        "name": "EN",
        "base_url": "https://tum-dev.github.io/eat-api/en/",
        "label": "English",
        "flag": "\ud83c\udff4\udb40\udc67\udb40\udc62\udb40\udc65\udb40\udc6e\udb40\udc67\udb40\udc7f"
    }
];

export default {
    view: function () {
        const onchange = e => {
            const language = e.target.value;
            changeLanguage(language);
            m.route.set(getHref({language}));
        };
        const isSelected = value => value.toLowerCase() === m.route.param("language").toLowerCase();

        return m("div", {class: "select is-small is-rounded"},
            m("select", {onchange, class: "ws-5"}, languages.map(({name, label, flag}) =>
                m("option", {value: name.toLowerCase(), selected: isSelected(name)}, `${flag} ${label}`)))
        );
    }
};
