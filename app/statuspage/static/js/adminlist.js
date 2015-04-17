function confirm_delete(item_title, delete_url) {
    bootbox.confirm("Delete '" + item_title + "'?", function (result) {
        if (result === true) {
            $.get(delete_url, null, function() {
                location.reload();
            })
        }
    })
}
