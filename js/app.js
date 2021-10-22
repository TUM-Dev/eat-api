var locations = ['fmi-bistro', 'ipp-bistro', 'mensa-arcisstr', 'mensa-garching', 'mensa-leopoldstr', 'mensa-lothstr',
    'mensa-martinsried', 'mensa-pasing', 'mensa-weihenstephan', 'stubistro-arcisstr', 'stubistro-goethestr',
    'stubistro-großhadern', 'stubistro-grosshadern', 'stubistro-rosenheim', 'stubistro-schellingstr',
    'stucafe-adalbertstr', 'stucafe-akademie-weihenstephan', 'stucafe-boltzmannstr', 'stucafe-garching',
    'stucafe-karlstr', 'stucafe-pasing', 'mediziner-mensa'];

var root = document.getElementById('app');
const urlParams = new URLSearchParams(window.location.search);
const mensa = urlParams.get('mensa');
var currentLocation;
if (mensa == null) {
    currentLocation = locations[3]; // Default to "mensa-garching"
} else {
    currentLocation = mensa;
}

var currentWeek = moment(new Date()).week();

var MenuData = {
    menu: null,
    error: '',
    fetch: function() {
        m.request({
            method: 'GET',
            url: currentLocation + '/' + (new Date()).getFullYear() + '/' + pad(currentWeek) + '.json',
            })
            .then(function(menu) {
                MenuData.error = "";
                MenuData.menu = menu;
            })
            .catch(function(e) {
                if (locations.includes(currentLocation)) {
                    MenuData.error = 'No menu found for calendar week ' + currentWeek + '. ¯\\_(ツ)_/¯' + currentLocation + '/' + (new Date()).getFullYear() + '/' + pad(currentWeek) + '.json';
                } else {
                    MenuData.error = 'A location with the id "' + currentLocation + '" does not exist.' +
                        'Possible ids are: ' + locations;
                    currentLocation = null;
                }
            })
        }
}

var LocationsDropdown = {
    view: function() {
        return m("div", {class: "dropdown"}, [
                            m("div", {class: "dropdown-trigger"},
                            m("button", {class: "button"},[
                                m("span", currentLocation),
                                m("span", {class: "icon icon-small"},
                                    m("i", {class: "fa fa-angle-down"}))
                            ])),
                            m("div", {class: "dropdown-menu", role: "menu"},
                                m("div", {class: "dropdown-content"},
                                    locations.map(function(loc) {
                                        return m('a', {
                                            href: '?mensa=' + loc, class: 'dropdown-item',
                                            onclick: function() {
                                                setLocation(loc);
                                            },
                                        }, loc);
                                    })))
                        ])
    }
}

var Day = {
    view: function(vnode) {
        return [vnode.attrs.dishes.map(function(dish) {
            return m("tr", [
                m("td", dish.name),
                m("td", getPrice(dish.prices, "students"))
            ])
        })]
    }
}

var Menu = {
    oninit: MenuData.fetch,
    view: function() {
        return MenuData.error ? [
            m("div", MenuData.error)
        ] : MenuData.menu ? m("div", 
                              m("table", {class: "table is-hoverable", style: "margin: 0 auto;"}, [
                                m("thead", m("tr", [m("th", "Dish"), m("th", "Price (students)")])),
                                m("tbody", MenuData.menu.days.map(function(day) {
                                    return [
                                        // add id 'today' to today's menu (if exists)
                                        moment(new Date(day.date)).isSame(new Date(), "day") ?
                                            m("tr", {id: "today"}, m("td", {class: "is-light", colspan: "2", style: ""}, m("b", getWeekday(new Date(day.date)) + ", " + new Date(day.date).toLocaleDateString()))) :
                                            // else
                                            m("tr", m("td", {class: "is-light", colspan: "2", style: ""}, m("b", getWeekday(new Date(day.date)) + ", " + day.date))),
                                        m(Day, {dishes: day.dishes})
                                    ]
                                }))
        ])) 
        : m("div", "Loading...")
    }
}

var App = {
    view: function() {
        return m("div", [m("div", [m(LocationsDropdown), m("a", {class: "button", href: "#today"}, "Today")]), 
                         m("div", {class: "has-text-centered"}, [
                             m("h1", {class: "title"}, currentLocation),
                             m(Menu)
                         ])])
    }
}


m.mount(root, App);

function setLocation(loc) {
    currentLocation = loc;
    MenuData.fetch();
}

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

function getWeekday(date) {
    // adopted from https://www.w3schools.com/jsref/jsref_getday.asp
    var weekday = new Array(7);
    weekday[0] =  "Sunday";
    weekday[1] = "Monday";
    weekday[2] = "Tuesday";
    weekday[3] = "Wednesday";
    weekday[4] = "Thursday";
    weekday[5] = "Friday";
    weekday[6] = "Saturday";

    return weekday[date.getDay()];
}

// https://stackoverflow.com/questions/8089875/show-a-leading-zero-if-a-number-is-less-than-10
function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}

var dropdown = document.querySelector('.dropdown');
dropdown.addEventListener('click', function(event) {
  event.stopPropagation();
  dropdown.classList.toggle('is-active');
});