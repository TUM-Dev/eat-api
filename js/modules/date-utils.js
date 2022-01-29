export function dateFromString(raw) {
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

export function dateToString(date) {
    return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`;
}

export function padNumber(n) {
    return String(n).padStart(2, "0");
}

/**
 * Source: https://www.w3resource.com/javascript-exercises/javascript-date-exercise-24.php
 * @param day
 * @returns {number}
 */
export function getWeek(day) {
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

export function copyDate(date) {
    return new Date(date.getTime());
}

/**
 * Create a new date with the time given on the same date as the given date
 *
 * @param {Date} date
 * @param {string} time Format has to be \d\d:\d\d
 */
export function getDateWithTime(date, time){
    const out = copyDate(date);

    const result = time.match(/(\d\d):(\d\d)/);
    const hours = parseInt(result[1]);
    const minutes = parseInt(result[2]);

    out.setHours(hours, minutes);
    return out;
}
