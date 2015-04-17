$(document).ready(function() {
    initTooltips();
    initComponentStatusClickSubmit();
    configureItemButtons();
    configureCreateIncidentButton();
});

function initTooltips() {
    $('[data-toggle="tooltip"]').tooltip('destroy').tooltip({'placement': 'top'});
}

function initComponentStatusClickSubmit() {
    $('.component-status-form').off().change(function() {
        var $this = $(this);
        var postUrl = $this.attr('action');
        var formContents = $this.serialize();

        console.log("Form contents: " + formContents);
        $.ajax({
            type: "POST",
            url: postUrl,
            data: formContents
        });
    })
}

function configureCreateIncidentButton() {
    $('#show-create-incident-button').off().click(function () {
        $('#create-incident-wrapper').removeClass('hidden');
        $(this).addClass('hidden');
    })
}

function configureItemButtons() {
    $('.delete-incident-button').each(function() {
        var $this = $(this);
        $this.off().click({incidentId: $this.data('incident-id')}, deleteIncident);
    });
}

function deleteIncident(event) {
    console.log("Deleting incident " + event.data.incidentId);
    bootbox.confirm("Delete incident? All related history will be deleted.", function (result) {
        if (result === true) {
            var $incidentList = $('#incident-list');
            var page_slug = $incidentList.data('page-slug');

            var postUrl = "/page/" + page_slug + "/admin/incidents/" + event.data.incidentId + "/delete";

            $.ajax({
                type: "POST",
                url: postUrl,
                success: function() {
                    removeIncidentItem(event.data.incidentId);
                }
            })
        }
    });
}

function removeIncidentItem(incidentId) {
    $('#incident-item-' + incidentId).remove();
    if ($('#incident-list').children().length === 0) {
        $('#no-incidents-notification').removeClass('hidden');
    }
}
