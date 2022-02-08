import m from "../external/mithril.module.js";

import {changeLanguage, languages, getLanguage} from "../modules/translation.js";

export default {
    view: function () {
        const onchange = e => {
            const language = e.target.value;
            changeLanguage(language);
        };
        const isSelected = value => value.toLowerCase() === getLanguage()?.name.toLowerCase();

        return m("div", {class: "select is-small is-rounded"},
            m("select", {onchange, class: "ws-5"}, languages.map(({name, label, flag}) =>
                m("option", {value: name.toLowerCase(), selected: isSelected(name)}, `${flag} ${label}`)))
        );
    }
};
