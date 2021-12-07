/*global m*/

// deprecated, will be removed with new API file
const ingredientLookup = {
    1: {symbol: "🎨", info: "with dyestuff"},
    2: {symbol: "🥫", info: "with preservative"},
    3: {symbol: "⚗", info: "with antioxidant"},
    4: {symbol: "🔬", info: "with flavor enhancers"},
    5: {symbol: "🔶", info: "sulphured"},
    6: {symbol: "⬛", info: "blackened olive"},
    7: {symbol: "🐝", info: "waxed"},
    8: {symbol: "🔷", info: "with phosphate"},
    9: {symbol: "🍬", info: "with sweeteners"},
    10: {symbol: "💊", info: "with a source of phenylalanine"},
    11: {symbol: "🍡", info: "with sugar and sweeteners"},
    13: {symbol: "🍫", info: "with cocoa-containing grease"},
    14: {symbol: "🍮", info: "with gelatin"},
    99: {symbol: "🍷", info: "with alcohol"},

    F: {symbol: "🌽", info: "meatless dish"},
    V: {symbol: "🥕", info: "vegan dish"},
    S: {symbol: "🐖", info: "with pork"},
    R: {symbol: "🐄", info: "with beef"},
    K: {symbol: "🐂", info: "with veal"},
    G: {symbol: "🐔", info: "with poultry"},
    W: {symbol: "🐗", info: "with wild meat"},
    L: {symbol: "🐑", info: "with lamb"},
    Kn: {symbol: "🧄", info: "with garlic"},
    Ei: {symbol: "🥚", info: "with chicken egg"},
    En: {symbol: "🥜", info: "with peanut"},
    Fi: {symbol: "🐟", info: "with fish"},
    Gl: {symbol: "🌾", info: "with gluten-containing cereals"},
    GlW: {symbol: "GlW", info: "with wheat"},
    GlR: {symbol: "GlR", info: "with rye"},
    GlG: {symbol: "GlG", info: "with barley"},
    GlH: {symbol: "GlH", info: "with oats"},
    GlD: {symbol: "GlD", info: "with spelt"},
    Kr: {symbol: "🦀", info: "with crustaceans"},
    Lu: {symbol: "Lu", info: "with lupines"},
    Mi: {symbol: "🥛", info: "with milk and lactose"},
    Sc: {symbol: "🥥", info: "with shell fruits"},
    ScM: {symbol: "ScM", info: "with almonds"},
    ScH: {symbol: "🌰", info: "with hazelnuts"},
    ScW: {symbol: "ScW", info: "with Walnuts"},
    ScC: {symbol: "ScC", info: "with cashew nuts"},
    ScP: {symbol: "ScP", info: "with pistachios"},
    Se: {symbol: "Se", info: "with sesame seeds"},
    Sf: {symbol: "Sf", info: "with mustard"},
    Sl: {symbol: "Sl", info: "with celery"},
    So: {symbol: "So", info: "with soy"},
    Sw: {symbol: "🔻", info: "with sulfur dioxide and sulfites"},
    Wt: {symbol: "🐙", info: "with mollusks"},

    GQB: {symbol: "GQB", info: "Certified Quality - Bavaria"},
    MSC: {symbol: "🎣", info: "Marine Stewardship Council"},
};

function getDishIngredients(selectedIngredients) {
    const selected = {};
    for (const k of selectedIngredients) {
        selected[k] = ingredientLookup[k];
    }
    return selected;
}

export default function modal() {
    let showIngredientsModal = false;

    return {
        view: function (vnode) {
            const {selectedIngredients} = vnode.attrs;
            let ingredients;
            if (selectedIngredients) {
                ingredients = getDishIngredients(selectedIngredients);
            } else {
                ingredients = ingredientLookup;
            }

            let modalClass = "modal";
            if (showIngredientsModal) {
                modalClass += " is-active";
            }

            return m("span", [
                m("span", {
                    class: "is-clickable", onclick: function () {
                        showIngredientsModal = true;
                    }
                }, vnode.children),
                m("div", {class: modalClass}, [
                    m("div", {
                        class: "modal-background", onclick: function () {
                            showIngredientsModal = false;
                        }
                    }),
                    m("div", {class: "modal-content"},
                        m("div", {class: "card"},
                            m("div", {class: "card-content"},
                                m("div", {class: "content"},
                                    m("table", {class: "table is-fullwidth"}, [
                                        m("thead",
                                            m("tr", [m("th", "Symbol"), m("th", "Description")])),
                                        m("tbody", Object.entries(ingredients).map(function (value) {
                                            return m("tr", [
                                                m("td", value[1].symbol),
                                                m("td", value[1].info)
                                            ]);
                                        })),
                                        m("tfoot", m("tr", [m("td", {class: "p-0"}), m("td", {class: "p-0"})]))
                                    ]))))),
                    m("button", {
                        class: "modal-close is-large", "aria-label": "close", onclick: function () {
                            showIngredientsModal = false;
                        }
                    })
                ])
            ]);
        }
    };
}

export function subline(ingredients){
    return ingredients.map(function (ingredient) {
        return m("span", {class: "mx-1 is-inline-block", title: ingredientLookup[ingredient].info}, ingredientLookup[ingredient].symbol);
    });
}
