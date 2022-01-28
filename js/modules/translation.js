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
            "no-menu-for-date": "There is no menu for {{date, datetime(weekday: long; year: numeric; month: long; day: numeric)}}",
            "location-invalid": "A location with the id {{location}} does not exist.",
            "closest-canteen": "Select closest canteen",
            "opened": "Opened from {{start}} to {{end}}",
            "mon": "Monday",
            "tue": "Tuesday",
            "wed": "Wednesday",
            "thu": "Thursday",
            "fri": "Friday",
            "weekday": "Weekday",
            "opens": "Opens",
            "closes": "Closes",
            "opening-hours": "Opening hours {{canteen}}",
            "text-color": "Text color",
            "opening-hours-0": "Black: The selected date is not today",
            "opening-hours-1": "Blue: canteen will open later today",
            "opening-hours-2": "Green: canteen is currently open",
            "opening-hours-3": "Red: canteen is already closed",
            "queue-status": "Current queue status",
            "queue-status-tooltip": "{{percent, number(maximumSignificantDigits: 2)}}%, Count: {{current}}",
            "info-labels": "Show and filter for labels",
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
            "no-menu-for-date": "Es gibt kein Menü für {{date, datetime(weekday: long; year: numeric; month: long; day: numeric)}}",
            "location-invalid": "Es gibt keine Mensa mit der ID {{location}}",
            "closest-canteen": "Nächstgelegene Mensa auswählen",
            "opened": "Geöffnet von {{start}} bis {{end}}",
            "mon": "Montag",
            "tue": "Dienstag",
            "wed": "Mittwoch",
            "thu": "Donnerstag",
            "fri": "Freitag",
            "weekday": "Wochentag",
            "opens": "Öffnet",
            "closes": "Schließt",
            "opening-hours": "Öffnungszeiten {{canteen}}",
            "text-color": "Farbe der Öffnungszeitenanzeige",
            "opening-hours-0": "Schwarz: Das ausgewählte Datum ist nicht heute",
            "opening-hours-1": "Blau: Die Mensa wird später öffnen",
            "opening-hours-2": "Grün: Die Mensa ist aktuell geöffnet",
            "opening-hours-3": "Rot: Die Mensa hat bereits geschlossen",
            "queue-status": "Aktuelle Mensa Auslastung",
            "queue-status-tooltip": "{{percent, number(maximumSignificantDigits: 2)}}%, Anzahl: {{current}}",
            "info-labels": "Zeige und filtere nach Zusatzstoffen",
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
