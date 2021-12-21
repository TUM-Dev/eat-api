import m from "../lib/mithril.module.js";

let labels = [];

function getLabelText(label) {
    const labelObject = labels.find(l => l["enum_name"] === label);
    if (!labelObject) {
        return label;
    }
    return labelObject["text"]["DE"];
}

export function modal() {
    let showModal = false;

    return {
        oninit: function () {
            // avoid multiple loadings, as this should not change
            if (labels.length === 0) {
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
            if (!selectedLabels){
                selectedLabels =  labels.map(l => l["enum_name"]);
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
                                            m("tr", [m("th", "Symbol"), m("th", "Description")])),
                                        m("tbody", selectedLabels.map(function (label) {
                                            return m("tr", [
                                                m("td", label),
                                                m("td", getLabelText(label))
                                            ]);
                                        })),
                                        m("tfoot", m("tr", [m("td", {class: "p-0"}), m("td", {class: "p-0"})]))
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
        return m("span", {class: "mx-1 is-inline-block", title: getLabelText(label)}, label);
    });
}
