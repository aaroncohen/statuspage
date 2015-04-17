var load_time = new Date();

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip({'placement': 'top'});

    update_time_text();
    setInterval(update_time_text, 15000);
});

function update_time_text() {
    $('#page-refreshed-time').text("Updated " + moment(load_time).fromNow());
}
