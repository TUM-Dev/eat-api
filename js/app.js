// hard-coded list of all canteens
var locations = ['fmi-bistro', 'ipp-bistro', 'mensa-arcisstr', 'mensa-garching', 'mensa-leopoldstr', 'mensa-lothstr',
    'mensa-martinsried', 'mensa-pasing', 'mensa-weihenstephan', 'stubistro-arcisstr', 'stubistro-goethestr',
    'stubistro-großhadern', 'stubistro-grosshadern', 'stubistro-rosenheim', 'stubistro-schellingstr',
    'stucafe-adalbertstr', 'stucafe-akademie-weihenstephan', 'stucafe-boltzmannstr', 'stucafe-garching',
    'stucafe-karlstr', 'stucafe-pasing', 'mediziner-mensa'];

var ingredients = {
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

var dateFormat = 'YYYY-MM-DD';

function getDate() {
    var date = m.route.param('date');
    if (date === undefined) {
        return moment();
    }
    return moment(date, dateFormat);
}

function Controls() {
    var LocationsDropdown = {
        view: function () {
            return m("div", {class: "field has-addons"}, [
                m("p", {class: "control"}, m("a", {class: "button"}, "Canteen")),
                m("p", {class: "control mw70"},
                    m("div", {class: "select"}, [
                        m("select", {
                            onchange: function (e) {
                                if (m.route.param('date')) {
                                    m.route.set('/:mensa/:date', {mensa: e.target.value, date: m.route.param('date')})
                                } else {
                                    m.route.set('/:mensa', {mensa: e.target.value})
                                }

                            }
                        }, locations.map(function (loc) {
                            var selected = loc === m.route.param("mensa");
                            return m("option", {value: loc, selected: selected}, loc);
                        }))
                    ])
                )
            ]);
        }
    };

    function DatePicker() {
        return {
            view: function () {
                var currentDate = getDate();

                var before = currentDate.clone().subtract(1, 'd').format(dateFormat);
                var after = currentDate.clone().add(1, 'd').format(dateFormat);

                var mensa = m.route.param('mensa');

                return m("div", {class: "field has-addons"}, [
                    m("p", {class: "control"},
                        m(m.route.Link, {href: `/${mensa}/${before}`, class: 'button'},
                            m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-angle-left"}))),
                    ),
                    m("p", {class: "control"},
                        m("input", {
                            type: "date", class: "input", value: currentDate.format(dateFormat), onchange: function (e) {
                                m.route.set('/:mensa/:date', {mensa: m.route.param('mensa'), date: e.target.value})
                            }
                        })
                    ),
                    m("p", {class: "control"},
                        m(m.route.Link, {href: `/${mensa}/${after}`, class: 'button'},
                            m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-angle-right"})))
                    ),
                ])
            }
        }
    }

    return {
        view: function () {
            return m("div", {class: 'columns is-justify-content-space-between'}, [
                m(LocationsDropdown),
                m(DatePicker)
            ]);
        }
    }
}

function Day() {
    function getPrice(prices, type) {
        if (prices.hasOwnProperty(type)) {
            var price = prices[type];
            if (price != null) {
                var priceStr = null;

                // Base price:
                var basePrice = parseFloat(price.base_price);
                if (!isNaN(basePrice) && basePrice > 0.0) {
                    priceStr = basePrice.toFixed(2) + '€';
                }

                // Unit per price:
                var pricePerUnit = parseFloat(price.price_per_unit);
                if (!isNaN(pricePerUnit) && pricePerUnit > 0.0 && price.unit != null) {
                    if (priceStr) {
                        priceStr += ' + ';
                    } else {
                        priceStr = '';
                    }
                    priceStr += pricePerUnit.toFixed(2) + '€/' + price.unit;
                }
                return priceStr;
            }
        }
        return "";
    }

    return {
        view: function (vnode) {
            console.log(vnode);
            return [vnode.attrs.dishes.map(function (dish) {
                return m("tr", [
                    m("td", [
                        m("p", dish.name),
                        m("span", {class: "is-size-7"}, dish.ingredients.map(function (ingredient) {
                            return m("span", {class: "mx-1", title: ingredients[ingredient].info}, ingredients[ingredient].symbol);
                        }))
                    ]),
                    m("td", getPrice(dish.prices, "students"))
                ])
            })]
        }
    }
}

var showIngredientsModal = false;

function Ingredients() {
    return {
        view: function () {
            var modalClass = "modal";
            if (showIngredientsModal) {
                modalClass += " is-active";
            }

            return m("span", [
                m("span", {
                    class: "icon icon-small is-clickable", onclick: function () {
                        showIngredientsModal = true
                    }
                }, m("i", {class: "fa fa-info-circle"})),
                m("div", {class: modalClass}, [
                    m("div", {
                        class: "modal-background", onclick: function () {
                            showIngredientsModal = false
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
                                            ])
                                        })),
                                        m("tfoot", m("tr", [m("td", {class: "p-0"}), m("td", {class: "p-0"})]))
                                    ]))))),
                    m("button", {
                        class: "modal-close is-large", "aria-label": "close", onclick: function () {
                            showIngredientsModal = false
                        }
                    })
                ])
            ]);
        }
    }
}

function Menu() {
    var MenuData = {
        currentParams: {},
        menu: null,
        error: '',
        fetch: function () {
            var currentDate = getDate();
            var params = {
                mensa: m.route.param('mensa'),
                year: currentDate.year(),
                week: currentDate.format('WW')
            };

            // if parameters have not changed, no new request is required
            if (MenuData.currentParams.mensa === params.mensa && MenuData.currentParams.year === params.year && MenuData.currentParams.week === params.week) {
                return;
            }
            MenuData.currentParams = params;

            m.request({
                method: 'GET',
                url: ':mensa/:year/:week.json',
                params: params
            })
                .then(function (menu) {
                    MenuData.error = "";
                    MenuData.menu = menu;
                })
                .catch(function (e) {
                    if (locations.includes(m.route.param('mensa'))) {
                        MenuData.error = 'No menu found for calendar week ' + currentDate.format('W') + '. ¯\\_(ツ)_/¯';
                    } else {
                        MenuData.error = 'A location with the id "' + m.route.param('mensa') + '" does not exist.' +
                            'Possible ids are: ' + locations;
                    }
                })
        }
    }

    return {
        oninit: MenuData.fetch,
        onupdate: MenuData.fetch,
        view: function () {
            function selectedDay(day) {
                return moment(day.date).isSame(getDate());
            }

            if (MenuData.error) {
                return m("div", MenuData.error);
            } else if (!MenuData.menu) {
                return m("div", "Loading...")
            }

            var menuOfTheDay = MenuData.menu.days.find(selectedDay);
            if (!menuOfTheDay) {
                return m("div", `There is no menu for ${moment(m.route.param("date")).format('dddd, L')}`);
            } else {
                return m("div",
                    m("table", {class: "table is-hoverable is-fullwidth"}, [
                        m("thead", m("tr", [
                            m("th", m("span", [
                                "Dish",
                                m(Ingredients)
                            ])),
                            m("th", "Price (students)")
                        ])),
                        m("tbody", [
                                m(Day, {dishes: menuOfTheDay.dishes})
                            ]
                        ),
                        m("tfoot", m("tr", [m("td", {class: "p-0"}), m("td", {class: "p-0"})]))
                    ])
                );
            }
        }
    }
}

var App = {
    view: function () {
        return m("div", {class: "columns is-centered"},
            m("div", {class: "column is-6-fullhd is-8-widescreen is-10-desktop is-12-touch"}, [
                m(Controls),
                m(Menu)
            ])
        );
    }
}

// mount mithril for auto updates
var root = document.getElementById('app');
var defaultCanteen = locations[3];
m.route(root, `/${defaultCanteen}`, {"/:mensa/:date": App, "/:mensa": App});
