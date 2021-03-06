// updater-button.js

var AssociatedId = function (clicked_button) {
    if (clicked_button != undefined) {
        let attachedParamChooser = $(clicked_button).parent().children("ul")[0];
        if (attachedParamChooser == undefined) {
            attachedParamChooser = $(clicked_button).parent().children("#minCr")[0];
        }
        return $(attachedParamChooser).attr('id');
    }
}

var GetUpdatedValues = function (updatedList) {
    if (updatedList != undefined) {
        let parent_list = $("#" + updatedList);
        var selected_elements = []
        for (var i = 0; i < parent_list.find("input").length; i++) {
            var this_box = parent_list.find("input")[i];
            if ($(this_box).prop("checked")) {
                selected_elements.push(this_box.id);
            }
        }
        window.localStorage.setItem(updatedList, selected_elements);
        return selected_elements;
    }
}

var floatify = function (number) {
    if (number.includes('/')) {
        var y = number.split('/');
        return (y[0] / y[1]);
    } else {
        return parseInt(number)
    }
}

var getUpdatedChallengeRatings = function () {
    var minValue = $("#minCr option:selected").attr("value");
    var maxValue = $("#maxCr option:selected").attr("value");
    var allowLegendary = $("#allowLegendary").prop("checked");
    var allowNamed = $("#allowNamed").prop("checked");
    let minValueComp = floatify(minValue)
    let maxValueComp = floatify(maxValue)
    var alerts = $("#challengeRatingSelectorDiv .alert")
    alerts.remove();
    if (maxValueComp < minValueComp) {
        $("#challengeRatingSelectorDiv").prepend('<div class="alert alert-danger" role="alert">Please ensure your minimum challenge rating is less than or equal to your maximum challenge rating.</div>')
        return;
    }
    window.localStorage.setItem("minCr", JSON.stringify(minValue))
    window.localStorage.setItem("maxCr", JSON.stringify(maxValue))
    window.localStorage.setItem("allowLegendary", JSON.stringify(allowLegendary))
    window.localStorage.setItem("allowNamed", JSON.stringify(allowNamed))
    return [minValue, maxValue, allowLegendary, allowNamed];
}

var sortTable = function (clicked_button) {
    var listUpdated = AssociatedId(clicked_button);
    if (listUpdated == "minCr") {
        var values = getUpdatedChallengeRatings();
        monsterParameters["minimumChallengeRating"] = values[0]
        monsterParameters["maximumChallengeRating"] = values[1]
        monsterParameters["allowLegendary"] = values[2]
        monsterParameters["allowNamed"] = values[3]
    } else {
        let listUpdatedName = listUpdated.split("_")[0];
        window.monsterParameters[listUpdatedName] = GetUpdatedValues(listUpdated);
    }
    window.monsterDataTable.ajax.reload();
    window.monsterDataTable.columns.adjust().draw();
}

var toggleAll = function (clicked_button) {
    let listUpdated = AssociatedId(clicked_button);
    let command = $(clicked_button).text()
    if (command == "Deselect All") {
        $('#' + listUpdated).find(":input").prop("checked", false)
        $(clicked_button).text("Select All");
    } else if (command == "Select All") {
        $('#' + listUpdated).find(":input").prop("checked", true)
        $(clicked_button).text("Deselect All");
    }
    window.monsterDataTable.ajax.reload();
    window.monsterDataTable.columns.adjust().draw();
}

module.exports = { GetUpdatedValues: GetUpdatedValues, AssociatedId: AssociatedId, getUpdatedChallengeRatings: getUpdatedChallengeRatings, floatify: floatify, sortTable: sortTable, toggleAll: toggleAll }
