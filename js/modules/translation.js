import m from "../external/mithril.module.js";
import i18next from "../external/i18next.module.js";
import i18nextBrowserLanguageDetector from "../external/i18nextBrowserLanguageDetector.module.js";
import {getHref} from "./url-utils.js";

// load languages from the API
export let languages = [];
m.request({
    method: "GET",
    url: "enums/languages.json"
}).then(function (result) {
    languages = result;
});

/*
 add hash detector, to get language from hash, set through mithril
 can not use mithril directly, as we want to set the default language based on the navigator language
 */
const hashDetector = {
    name: "hashDetector",

    lookup(options) {
        const hash = window.location.hash;
        if (options.hashStart > hash.length) {
            return;
        }

        return hash.substr(options.hashStart, options.hashLength);
    },
};

const languageDetector = new i18nextBrowserLanguageDetector();
languageDetector.addDetector(hashDetector);

const resources = {
    en: {
        translation: {
            "dish": "Dish",
            "price": "Price (students)",
            "symbol": "Symbol",
            "description": "Description",
            "hide": "hide",
            "subtitle": "Simple static API for some (student) food places in Munich.",
            "important": "Important",
            "disclaimer": "This page shows the menus of the current week in a human-readable format. If you are searching for how to use the API, please take a look at the",
            "loading": "Loading",
            "no-menu-for-week": "No menu found for calendar week {{week}} in {{canteen}}",
            "no-menu-for-date": "There is no menu for {{date}}",
            "location-invalid": "A location with the id {{location}} does not exist.",
            "closest-canteen": "Select closest canteen",
        }
    },
    de: {
        translation: {
            "dish": "Gericht",
            "price": "Preis (Studenten)",
            "symbol": "Symbol",
            "description": "Beschreibung",
            "hide": "Verbergen",
            "subtitle": "Einfache statische API für einige (studentische) Mensen in München.",
            "important": "Wichtig",
            "disclaimer": "Diese Seite zeigt die Menüs der aktuellen Woche in einem für Menschen lesbaren Format. Wenn Sie wissen möchten, wie Sie die API verwenden können, schauen Sie bitte in die",
            "loading": "Lädt",
            "no-menu-for-week": "Kein Menü für Kalenderwoche {{week}} in {{canteen}} gefunden",
            "no-menu-for-date": "Es gibt kein Menü für {{date}}",
            "location-invalid": "Es gibt keine Mensa mit der ID {{location}}",
            "closest-canteen": "Nächstgelegene Mensa auswählen",
        }
    }
};

i18next
    .use(languageDetector)
    .init({
        fallbackLng: "en",
        detection: {
            order: ["hashDetector", "navigator"],
            hashStart: 3, // assumption: when given, the language is always at this position
            hashLength: 2,
        },
        resources
    });

export default i18next.t;

export const defaultLanguage = i18next.resolvedLanguage;

export function getLanguage(){
    const language = m.route.param("language");
    return languages.find(l => l.name.toLowerCase() === language.toLowerCase());
}

export function changeLanguage(language) {
    const lowercase = language.toLowerCase();

    m.route.set(getHref({language: lowercase}));
    i18next.changeLanguage(lowercase);
}
