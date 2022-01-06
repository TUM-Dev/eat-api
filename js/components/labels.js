import m from "../external/mithril.module.js";
import translate, {getLanguage} from "../modules/translation.js";
import {getHref, getFilterLabels} from "../modules/url-utils.js";

let labels = [];
let labelsLoadInitiated = false;

function hideLabelCheckbox() {
    function onchange(e) {
        const {checked, value} = e.target;

        // set new filters
        let filter = [...getFilterLabels()];
        if (checked) {
            filter.push(value);
        } else {
            filter = filter.filter(v => v !== value);
        }

        // apply new url
        const href = getHref({filter});
        m.route.set(href);
    }

    return {
        view: function (vnode) {
            const filters = getFilterLabels();
            const {value, disabled} = vnode.attrs;
            const checked = filters && filters.indexOf(value) !== -1;
            return m("input", {type: "checkbox", onchange, value, checked, disabled});
        }
    };
}

/**
 * Returns the dishes to show and to hide for the given dishes in accordance with the filters set
 *
 * @param allDishes
 * @returns {{hide: *, show: *}}
 */
export function getFilteredDishes(allDishes) {
    /**
     * Filter dish, if it includes one of the ingredients to be excluded
     *
     * @param dish
     * @returns {boolean}
     */
    function filterDishes(dish) {
        return !filter.some(f => dish.labels.indexOf(f) !== -1);
    }

    const filter = getFilterLabels();
    // filter all dishes, which are hidden through the filters
    const show = allDishes.filter(filterDishes);
    const hide = allDishes.filter(dish => !filterDishes(dish));
    return {show, hide};
}

function getLabelObject(label){
    return labels.find(l => l["enum_name"] === label);
}

function getLabelText(label) {
    const language = getLanguage();
    const languageIdentifier = language["name"];

    const labelObject = getLabelObject(label);
    if (!labelObject) {
        return label;
    }
    return labelObject["text"][languageIdentifier];
}

function getLabelAbbreviation(label){
    const labelObject = getLabelObject(label);
    if (!labelObject || !labelObject["abbreviation"]) {
        return label;
    }
    return labelObject["abbreviation"];
}

export function modal() {
    let showModal = false;

    return {
        oninit: function () {
            // avoid multiple loadings, as this should not change
            if (!labelsLoadInitiated) {
                labelsLoadInitiated = true;

                m.request({
                    method: "GET",
                    url: "enums/labels.json"
                }).then(function (result) {
                    labels = result;
                });
            }
        },
        view: function (vnode) {
            let {selectedLabels} = vnode.attrs;
            const {readOnly} = vnode.attrs;
            if (!selectedLabels){
                selectedLabels = labels.map(l => l["enum_name"]);
            }

            let modalClass = "modal";
            if (showModal) {
                modalClass += " is-active";
            }

            return m("span", [
                m("span", {
                    class: "is-clickable", onclick: function () {
                        showModal = true;
                    }
                }, vnode.children),
                m("div", {class: modalClass}, [
                    m("div", {
                        class: "modal-background", onclick: function () {
                            showModal = false;
                        }
                    }),
                    m("div", {class: "modal-content"},
                        m("div", {class: "card"},
                            m("div", {class: "card-content"},
                                m("div", {class: "content"},
                                    m("table", {class: "table is-fullwidth"}, [
                                        m("thead",
                                            m("tr", [m("th", translate("symbol")), m("th", translate("description")), m("th", translate("hide"))])),
                                        m("tbody", selectedLabels.map(function (label) {
                                            return m("tr", [
                                                m("td", getLabelAbbreviation(label)),
                                                m("td", getLabelText(label)),
                                                m("td", m(hideLabelCheckbox, {value: label, disabled: readOnly})),
                                            ]);
                                        })),
                                        m("tfoot", m("tr", [m("td", {class: "p-0"}), m("td", {class: "p-0"}), m("td", {class: "p-0"})]))
                                    ]))))),
                    m("button", {
                        class: "modal-close is-large", "aria-label": "close", onclick: function () {
                            showModal = false;
                        }
                    })
                ])
            ]);
        }
    };
}

export function subline(labels) {
    if (!labels) {
        return;
    }

    return labels.map(function (label) {
        return m("span", {class: "mx-1 is-inline-block", title: getLabelText(label)}, getLabelAbbreviation(label));
    });
}
