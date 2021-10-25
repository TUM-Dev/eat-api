// hard-coded list of all canteens
var locations = ['fmi-bistro', 'ipp-bistro', 'mensa-arcisstr', 'mensa-garching', 'mensa-leopoldstr', 'mensa-lothstr',
    'mensa-martinsried', 'mensa-pasing', 'mensa-weihenstephan', 'stubistro-arcisstr', 'stubistro-goethestr',
    'stubistro-großhadern', 'stubistro-grosshadern', 'stubistro-rosenheim', 'stubistro-schellingstr',
    'stucafe-adalbertstr', 'stucafe-akademie-weihenstephan', 'stucafe-boltzmannstr', 'stucafe-garching',
    'stucafe-karlstr', 'stucafe-pasing', 'mediziner-mensa'];

var LocationsDropdown = {
    view: function () {
        return m("div", {
            class: "dropdown", onclick: function (event) {
                event.stopPropagation();
                this.classList.toggle('is-active');
            }
        }, [
            m("div", {class: "dropdown-trigger"},
                m("button", {class: "button"}, [
                    m("span", m.route.param('mensa')),
                    m("span", {class: "icon icon-small"},
                        m("i", {class: "fa fa-angle-down"}))
                ])),
            m("div", {class: "dropdown-menu", role: "menu"},
                m("div", {class: "dropdown-content"},
                    locations.map(function (loc) {
                        return m(m.route.Link, {
                            href: `/${loc}`,
                            class: 'dropdown-item',
                        }, loc);
                    })))
        ])
    }
}

var DatePicker = {
    view: function () {
        return m(m.route.Link, {href: '', class: 'button',}, "Today");
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
            var currentDate = moment(m.route.param('date'), 'YYYY-MM-DD');
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
            return MenuData.error ? [
                m("div", MenuData.error)
            ] : MenuData.menu ? m("div",
                    m("table", {class: "table is-hoverable", style: "margin: 0 auto;"}, [
                        m("thead", m("tr", [m("th", "Dish"), m("th", "Price (students)")])),
                        m("tbody", MenuData.menu.days.map(function (day) {
                            return [
                                m("tr", m("td", {class: "is-light", colspan: "2", style: ""}, m("b", moment(day.date).format('dddd, L')))),
                                m(Day, {dishes: day.dishes})
                            ]
                        }))
                    ]))
                : m("div", "Loading...")
        }
    }
}

var App = {
    view: function () {
        return m("div", [m("div", [m(LocationsDropdown), m(DatePicker)]),
            m("div", [
                m("h1", {class: ["title has-text-centered"]}, m.route.param('mensa')),
                m(Menu)
            ])])
    }
}

// mount mithril for auto updates
var root = document.getElementById('app');
var defaultCanteen = locations[3];
var defaultDate = moment().format('YYYY-MM-DD');
m.route(root, `/${defaultCanteen}/${defaultDate}`, {"/:mensa/:date": App});
