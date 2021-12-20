import m from "./lib/mithril.module.js";

import DateSelection from "./components/date-selection.js";
import LocationSelection from "./components/location-selection.js";
import Menu from "./components/menu.js";

function Controls() {
    return {
        view: function () {
            return m("div", {class: "columns is-justify-content-space-between"}, [
                m(LocationSelection),
                m(DateSelection)
            ]);
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
