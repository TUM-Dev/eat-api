/*global m, L*/
// external global variables: m (Mithril), L (Leaflet)

let labels = [];

function getLabelText(label){
    const labelObject = labels.find(l => l["enum_name"] === label);
    if (!labelObject){
        return label;
    }
    return labelObject["text"]["DE"];
}

function dateFromString(raw) {
    const datePattern = /^(\d{4})-(\d{2})-(\d{2})$/;
    if (raw === undefined || !raw.match(datePattern)) {
        const d = new Date();
        // remove all time parameters, for easier comparing
        d.setHours(0, 0, 0, 0);
        return d;
    }

    const [, year, month, day] = datePattern.exec(raw);
    return new Date(year, month - 1, day);
}

function padNumber(n) {
    return String(n).padStart(2, "0");
}

function dateToString(date) {
    return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`;
}

/**
 * Source: https://www.w3resource.com/javascript-exercises/javascript-date-exercise-24.php
 * @param day
 * @returns {number}
 */
function getWeek(day) {
    // copy to work on
    const tdt = new Date(day.getTime());

    // get thursday of the current week
    const dayn = (day.getDay() + 6) % 7;
    tdt.setDate(tdt.getDate() - dayn + 3);
    const thursdayOfWeek = tdt.valueOf();

    // get the first thursday of the year
    tdt.setMonth(0, 1);
    if (tdt.getDay() !== 4) {
        tdt.setMonth(0, 1 + ((4 - tdt.getDay()) + 7) % 7);
    }

    // difference between thursdays is the week number
    const week = 1 + Math.ceil((thursdayOfWeek - tdt) / 604800000);
    const year = tdt.getFullYear();
    return {week, year};
}

function copyDate(date) {
    return new Date(date.getTime());
}

function getHref({mensa, date}) {
    if (mensa === undefined) {
        mensa = m.route.param("mensa");
    }

    if (date === undefined && m.route.param("date")) {
        date = m.route.param("date");
    }

    const parts = [mensa, date];
    return `/${parts.filter(p => p).join("/")}`;
}

function Controls() {
    let showModal = false;
    let canteens = [];

    function openStreetMap() {
        return {
            oncreate: function (vnode) {
                // disable tap handler, to fix a bug when opening popups on iOS closes them immediately again (https://github.com/Leaflet/Leaflet/issues/7255)
                const map = L.map(vnode.dom, {tap: false})
                    .setView([48.15, 11.55], 10); // coordinates for munich
                L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                    attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors"
                }).addTo(map);

                this.map = map;
            },
            onbeforeupdate: function () {
                // bugfix for not loading map: https://stackoverflow.com/a/53511529/319711
                this.map.invalidateSize();

                // init or clear markers group
                if (this.markers === undefined) {
                    this.markers = L.layerGroup();
                    this.map.addLayer(this.markers);
                } else {
                    this.markers.clearLayers();
                }

                const self = this;
                canteens.map(function (c) {
                    // create mithril links to canteens
                    const linkContent = [
                        m("b", c.name),
                        m("span", {class: "icon"}, m("i", {class: "fa fa-external-link"}))
                    ];
                    const link = m(m.route.Link, {href: getHref({mensa: c.canteen_id})}, linkContent);

                    // render element manually, since it needs to be displayed inside of leaflet, not mithril
                    const div = document.createElement("div");
                    m.render(div, link);

                    const marker = L.marker([c.location.latitude, c.location.longitude])
                        .bindPopup(`${div.innerHTML} <br> ${c.location.address}`);

                    self.markers.addLayer(marker);

                    // change color of active marker, by adding a specific css class; needs to be done after addLayer
                    if (c.canteen_id === m.route.param("mensa")) {
                        marker._icon.classList.add("active-marker");
                    }
                });
            },
            view: function () {
                return m("div", {id: "map"});
            }
        };
    }

    function mapModal() {
        return {
            view: function () {
                return [
                    m("span", {
                        class: "button", onclick: function () {
                            showModal = true;
                        }
                    }, [m("span", {class: "icon"}, m("i", {class: "fa fa-map"}))
                    ]),
                    m("div", {class: `modal ${showModal ? "is-active" : ""}`}, [
                        m("div", {
                            class: "modal-background", onclick: function () {
                                showModal = false;
                            }
                        }),
                        m("div", {class: "modal-content map-modal"},
                            m("div", {class: "card"},
                                m("div", {class: "card-content"},
                                    m("div", {class: "content"},
                                        m(openStreetMap))))),
                        m("button", {
                            class: "modal-close is-large", "aria-label": "close", onclick: function () {
                                showModal = false;
                            }
                        })
                    ])
                ];
            }
        };
    }

    let searchingForLocation = false;

    function selectedClosestCanteen() {
        if (navigator.geolocation) {
            searchingForLocation = true;
            navigator.geolocation.getCurrentPosition(function (position) {
                const leafletPosition = L.latLng({lat: position.coords.latitude, lng: position.coords.longitude});
                const canteenDistances = canteens
                    .map(c => ({c, p: L.latLng({lat: c.location.latitude, lng: c.location.longitude})})) // convert to leaflet points
                    .map(({c, p}) => ({c, d: leafletPosition.distanceTo(p)})) // calculate distances
                    .sort((a, b) => a.d - b.d); // order ascending

                const mensa = canteenDistances[0].c.canteen_id;
                m.route.set(getHref({mensa}));

                searchingForLocation = false;
            }, function (e) {
                alert(`Geolocation could not be obtained: ${e.message}`);

                searchingForLocation = false;
                m.redraw(); // needed, as mithril has no auto update, for async state changes
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }

    const LocationsDropdown = {
        oninit: function () {
            m.request({
                method: "GET",
                url: "enums/canteens.json"
            }).then(function (result) {
                canteens = result;
            });
        },
        view: function () {
            return m("div", {class: "field has-addons"}, [
                m("p", {class: "control"},
                    m("div", {class: "select mw230"}, [
                        m("select", {
                            onchange: function (e) {
                                m.route.set(getHref({mensa: e.target.value}));
                            }
                        }, canteens.map(function (c) {
                            const selected = c.canteen_id === m.route.param("mensa");
                            return m("option", {value: c.canteen_id, selected}, c.name);
                        }))
                    ])
                ),
                m("p", {class: "control"},
                    m("span", {
                        class: "button",
                        title: "Selected closest canteen.",
                        onclick: selectedClosestCanteen,
                        disabled: searchingForLocation
                    }, [
                        m("span", {class: "icon"}, m("i", {class: `fa ${searchingForLocation ? "fa-spinner fa-spin" : "fa-location-arrow"}`}))
                    ])
                ),
                m("p", {class: "control"},
                    m(mapModal)
                ),
            ]);
        }
    };

    function DatePicker() {
        return {
            view: function () {
                const currentDate = dateFromString(m.route.param("date"));

                const before = copyDate(currentDate);
                before.setDate(before.getDate() - 1);
                const after = copyDate(currentDate);
                after.setDate(after.getDate() + 1);

                const mensa = m.route.param("mensa");

                return m("div", {class: "field has-addons"}, [
                    m("p", {class: "control"},
                        m(m.route.Link, {href: getHref({mensa, date: dateToString(before)}), class: "button"},
                            m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-angle-left"}))),
                    ),
                    m("p", {class: "control"},
                        m("input", {
                            type: "date", class: "input", value: dateToString(currentDate), onchange: function (e) {
                                m.route.set(getHref({date: e.target.value}));
                            }
                        })
                    ),
                    m("p", {class: "control"},
                        m(m.route.Link, {href: getHref({mensa, date: dateToString(after)}), class: "button"},
                            m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-angle-right"})))
                    ),
                ]);
            }
        };
    }

    return {
        view: function () {
            return m("div", {class: "columns is-justify-content-space-between"}, [
                m(LocationsDropdown),
                m(DatePicker)
            ]);
        }
    };
}

function Day() {
    function getPrice(prices, type) {
        if (Object.prototype.hasOwnProperty.call(prices, type)) {
            const price = prices[type];
            if (price != null) {
                let priceStr = null;

                // Base price:
                const basePrice = parseFloat(price.base_price);
                if (!isNaN(basePrice) && basePrice > 0.0) {
                    priceStr = basePrice.toFixed(2) + "€";
                }

                // Unit per price:
                const pricePerUnit = parseFloat(price.price_per_unit);
                if (!isNaN(pricePerUnit) && pricePerUnit > 0.0 && price.unit != null) {
                    if (priceStr) {
                        priceStr += " + ";
                    } else {
                        priceStr = "";
                    }
                    priceStr += pricePerUnit.toFixed(2) + "€/" + price.unit;
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
                    m("td", [
                        m("p", dish.name),
                        m(Labels, {labels: dish.labels},
                            m("span", {class: "is-size-7"}, dish.labels.map(function (label) {
                                return m("span", {class: "mx-1 is-inline-block", title: getLabelText(label)}, label);
                            }))
                        )
                    ]),
                    m("td", getPrice(dish.prices, "students"))
                ]);
            })];
        }
    };
}

function Labels() {
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
            const labels = vnode.attrs.labels;

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
                                        m("tbody", labels.map(function (label) {
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

function Menu() {
    const MenuData = {
        currentParams: {},
        menu: null,
        error: "",
        fetch: function () {
            const currentDate = dateFromString(m.route.param("date"));
            const {week, year} = getWeek(currentDate);
            const params = {
                mensa: m.route.param("mensa"),
                year,
                week: padNumber(week)
            };

            // if parameters have not changed, no new request is required
            if (MenuData.currentParams.mensa === params.mensa && MenuData.currentParams.year === params.year && MenuData.currentParams.week === params.week) {
                return;
            }
            MenuData.currentParams = params;

            m.request({
                method: "GET",
                url: ":mensa/:year/:week.json",
                params: params
            })
                .then(function (menu) {
                    MenuData.error = "";
                    MenuData.menu = menu;
                })
                .catch(function () {
                    MenuData.error = `No menu found for calendar week ${getWeek(currentDate).week} for canteen ${m.route.param("mensa")} . ¯\\_(ツ)_/¯`;
                });
        }
    };

    return {
        oninit: MenuData.fetch,
        onupdate: MenuData.fetch,
        view: function () {
            function selectedDay(day) {
                return dateFromString(m.route.param("date")).valueOf() === dateFromString(day.date).valueOf();
            }

            if (MenuData.error) {
                return m("div", MenuData.error);
            } else if (!MenuData.menu) {
                return m("div", "Loading...");
            }

            const menuOfTheDay = MenuData.menu.days.find(selectedDay);
            if (!menuOfTheDay) {
                return m("div", `There is no menu for ${dateFromString(m.route.param("date"))}`);
            } else {
                return m("div",
                    m("table", {class: "table is-hoverable is-fullwidth"}, [
                        m("thead", m("tr", [
                            m("th", m("span", [
                                "Dish",
                                m(Labels, {labels: labels.map(l => l["enum_name"])}, m("span", {class: "icon icon-small"}, m("i", {class: "fa fa-info-circle"})))
                            ])),
                            m("th", "Price (students)")
                        ])),
                        m("tbody", [
                            m(Day, {dishes: menuOfTheDay.dishes})
                        ]),
                        m("tfoot", m("tr", [m("td", {class: "p-0"}), m("td", {class: "p-0"})]))
                    ])
                );
            }
        }
    };
}

const App = {
    view: function () {
        return m("div", {class: "columns is-centered"},
            m("div", {class: "column is-6-fullhd is-8-widescreen is-10-desktop is-12-touch"}, [
                m(Controls),
                m(Menu)
            ])
        );
    }
};

// mount mithril for auto updates
const root = document.getElementById("app");
const defaultCanteen = "mensa-garching"; // since canteens.json is loaded asynchronously, hard code default canteen
m.route(root, `/${defaultCanteen}`, {"/:mensa/:date": App, "/:mensa": App});
