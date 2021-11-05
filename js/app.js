// hard-coded list of all canteens
var locations = ['fmi-bistro', 'ipp-bistro', 'mensa-arcisstr', 'mensa-garching', 'mensa-leopoldstr', 'mensa-lothstr',
    'mensa-martinsried', 'mensa-pasing', 'mensa-weihenstephan', 'stubistro-arcisstr', 'stubistro-goethestr',
    'stubistro-großhadern', 'stubistro-grosshadern', 'stubistro-rosenheim', 'stubistro-schellingstr',
    'stucafe-adalbertstr', 'stucafe-akademie-weihenstephan', 'stucafe-boltzmannstr', 'stucafe-garching',
    'stucafe-karlstr', 'stucafe-pasing', 'mediziner-mensa'];

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
                                if(m.route.param('date')){
                                    m.route.set('/:mensa/:date', {mensa: e.target.value, date: m.route.param('date')})
                                }else{
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
            return [vnode.attrs.dishes.map(function (dish) {
                return m("tr", [
                    m("td", dish.name),
                    m("td", getPrice(dish.prices, "students"))
                ])
            })]
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
                        m("thead", m("tr", [m("th", "Dish"), m("th", "Price (students)")])),
                        m("tbody", [
                                m(Day, {dishes: menuOfTheDay.dishes})
                            ]
                        )
                    ]));
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
