import m from "../external/mithril.module.js";

export default function Modal() {
    let showModal = false;

    return {
        view: function (vnode) {
            let modalClass = "modal";
            if (showModal) {
                modalClass += " is-active";
            }

            return m("span", [
                m("span", {class: "is-clickable", onclick: () => showModal = true}, vnode.children),
                m("div", {class: modalClass}, [
                    m("div", {class: "modal-background", onclick: () => showModal = false}),
                    m("div", {class: "modal-content"},
                        m("div", {class: "card"},
                            m("div", {class: "card-content"},
                                m("div", {class: "content"},
                                    vnode.attrs.content
                                )))),
                    m("button", {class: "modal-close is-large", "aria-label": "close", onclick: () => showModal = false})
                ])
            ]);
        }
    };
}
