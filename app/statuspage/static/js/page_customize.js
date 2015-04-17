$(document).ready(function() {
    initTooltips();

    var $name = $('#name');
    var $slug = $('#slug');

    $name.off().on('input', function() {
        $slug.val(string_to_slug($name.val()));
    });
});

function initTooltips() {
    $('[data-toggle="tooltip"]').tooltip('destroy').tooltip({'placement': 'top'});
}
