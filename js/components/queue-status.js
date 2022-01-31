import m from "../external/mithril.module.js";
import {getCanteen} from "./location-selection.js";
import translate from "../modules/translation.js";
import Tooltip from "./tooltip.js";
import {getCurrentState} from "./opening-hours.js";

export default function QueueStatus() {
    let fetchedCanteen;
    let status;

    function fetchQueue() {
        const canteen = getCanteen();

        // don't refetch, if canteen is the same
        if (fetchedCanteen === canteen) {
            return;
        }
        fetchedCanteen = canteen;

        if (!canteen.queue_status) {
            status = undefined;
            return;
        }

        m.request({
            method: "GET",
            url: canteen.queue_status
        }).then(function (result) {
            status = result;
        });
    }

    return {
        oninit: fetchQueue,
        onupdate: fetchQueue,
        view: function () {
            // show current status only, when canteen is open
            const {status: canteenStatus} = getCurrentState();
            if (canteenStatus !== 2) {
                return;
            }

            if (status && status.percent) {
                let progressColor;
                if (status.percent < 33) {
                    progressColor = "is-success";
                } else if (status.percent < 66) {
                    progressColor = "is-warning";
                } else {
                    progressColor = "is-danger";
                }

                return m("p", {class: "is-flex is-align-items-center"}, [
                    m("p", {class: "is-flex-shrink-0 mr-2"}, translate("queue-status")),
                    m(Tooltip, {class: "is-flex-grow-1", tooltip: translate("queue-status-tooltip", {percent: status.percent, current: status.current})},
                        m("progress", {class: `progress ${progressColor}`, value: status.percent, max: 100}, status.percent))
                ]);
            }
        }
    };
}
