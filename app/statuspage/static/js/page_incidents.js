$(document).ready(function() {
    initTooltips();
});

function initTooltips() {
    $('[data-toggle="tooltip"]').tooltip('destroy').tooltip({'placement': 'top'});
}
