import i18next from "../external/i18next.module.js";
import i18nextBrowserLanguageDetector from "../external/i18nextBrowserLanguageDetector.module.js";

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

i18next
    .use(languageDetector)
    .init({
        fallbackLng: "en",
        detection: {
            order: ["hashDetector", "navigator"],
            hashStart: 3, // assumption: when given, the language is always at this position
            hashLength: 2,
        },
        resources: {
            en: {
                translation: {
                }
            },
            de: {
                translation: {
                }
            }
        }
    });

export default i18next.t;

export const defaultLanguage = i18next.resolvedLanguage;

export const changeLanguage = i18next.changeLanguage;
