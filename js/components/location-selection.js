import L from "../external/leaflet.module.js";
import m from "../external/mithril.module.js";
import {getHref} from "../modules/url-utils.js";
import translate from "../modules/translation.js";
import Modal from "./modal.js";

export let canteens = [];

export function getCanteen(){
    const canteen = m.route.param("mensa");
    return canteens.find(v => v.canteen_id === canteen);
}

export function getCanteen(){
    const canteen = m.route.param("mensa");
    return canteens.find(v => v.canteen_id === canteen);
}

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

export default function LocatioSelection() {
    return {
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
                        title: translate("closest-canteen"),
                        onclick: selectedClosestCanteen,
                        disabled: searchingForLocation
                    }, [
                        m("span", {class: "icon"}, m("i", {class: `fa ${searchingForLocation ? "fa-spinner fa-spin" : "fa-location-arrow"}`}))
                    ])
                ),
                m("p", {class: "control map-modal"},
                    m(Modal, {content: m(openStreetMap)}, m("span", {class: "button"}, m("span", {class: "icon"}, m("i", {class: "fa fa-map"})))),
                ),
            ]);
        }
    };
}
