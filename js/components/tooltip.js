import m from "../external/mithril.module.js";

export default function Tooltip() {
    return {
        view: function (vnode) {
            if (!vnode.attrs.tooltip){
                return vnode.children;
            }

            const additionalClass = vnode.attrs.class ?? "";
            return m("div", {class: `${additionalClass} has-tooltip`, title: vnode.attrs.tooltip}, vnode.children);
        }
    };
}
