import m from "../external/mithril.module.js";
import {getCanteen} from "./location-selection.js";
import translate from "../modules/translation.js";

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
            if (status && status.percent) {
                let progressColor;
                if (status.percent < 33){
                    progressColor = "is-success";
                } else if (status.percent < 66){
                    progressColor = "is-warning";
                } else {
                    progressColor = "is-danger";
                }

                return m("p", {class: "is-flex is-align-items-center"}, [
                    m("p", {class: "is-flex-shrink-0 mr-2"}, translate("queue-status")),
                    m("progress", {class: `progress ${progressColor}`, value: status.percent, max: 100}, status.percent)
                ]);
            }
        }
    };
}
