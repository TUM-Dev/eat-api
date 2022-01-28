import m from "../external/mithril.module.js";

export default function Tooltip() {
    return {
        view: function (vnode) {
            return m("div", {class: `${vnode.attrs.class} has-tooltip`, title: vnode.attrs.tooltip}, vnode.children);
        }
    };
}
