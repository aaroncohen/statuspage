$(document).ready(function() {
    configureItemButtons();
});

function configureItemButtons() {
    $('.delete-page-button').each(function() {
        var $this = $(this);
        $this.off().click({pageSlug: $this.data('page-slug')}, deletePage);
    });
}

function deletePage(event) {
    console.log("Deleting page " + event.data.pageSlug);
    bootbox.confirm("Delete page? You will lose all of the associated incident history.", function (result) {
        if (result === true) {
            var postUrl = "/page/" + event.data.pageSlug + "/admin/delete";

            $.ajax({
                type: "POST",
                url: postUrl,
                success: function () {
                    removePageItem(event.data.pageSlug);
                }
            })
        }
    });
}

function removePageItem(pageSlug) {
    $('#item-' + pageSlug).remove();
    if ($('#page-list').children().length === 0) {
        $('#no-pages-notification').removeClass('hidden');
    }
}
