import m from "../external/mithril.module.js";
import t from "../modules/translation.js";

export default function Translate(text) {
    return {
        view: function () {
            return m("span", t(text));
        }
    };
}
