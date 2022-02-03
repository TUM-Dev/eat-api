import m from "./external/mithril.module.js";

import DateSelection from "./components/date-selection.js";
import LocationSelection from "./components/location-selection.js";
import LanguageSelection from "./components/language-selection.js";
import QueueStatus from "./components/queue-status.js";
import OpeningHours from "./components/opening-hours.js";

import Menu from "./components/menu.js";
import Translate from "./components/translate.js";

import {defaultLanguage} from "./modules/translation.js";

function Controls() {
    return {
        view: function () {
            return m("div", {class: "mb-3"}, [
                m("div", {class: "is-flex is-flex-wrap-wrap is-justify-content-space-between is-column-gap-4"}, [
                    m("div", {class: "is-flex-grow-1 is-flex-basis-half mb-4"}, m(LocationSelection)),
                    m("div", {class: "is-flex-grow-1 mb-4"}, m(DateSelection)),
                ]),
                m(OpeningHours),
                m(QueueStatus),
            ]);
        }
    };
}


const App = {
    view: function () {
        return m("div", {class: "columns is-centered"},
            m("div", {class: "column is-6-fullhd is-8-widescreen is-10-desktop is-12-touch"}, [
                m(Controls),
                m(Menu),
            ])
        );
    }
};

// mount mithril for auto updates
const root = document.getElementById("app");
const defaultCanteen = "mensa-garching"; // since canteens.json is loaded asynchronously, hard code default canteen
m.route(root, `/${defaultLanguage}/${defaultCanteen}`, {"/:language/:mensa/:date": App, "/:language/:mensa": App});

// mount language components
m.mount(document.getElementById("language-select"), LanguageSelection);
m.mount(document.getElementById("subtitle"), Translate("subtitle"));
m.mount(document.getElementById("important"), Translate("important"));
m.mount(document.getElementById("disclaimer"), Translate("disclaimer"));
