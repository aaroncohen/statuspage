$(document).ready(function() {
    initPage();
});

function initPage() {
    initSortableList();

    configureAddBoxButtons();
    configureItemButtons();

    initTooltips();
    initComponentStatusClickSubmit();
}

function initTooltips() {
    $('[data-toggle="tooltip"]').tooltip('destroy').tooltip({'placement': 'top'});
}

function initSortableList() {
    var $componentList = $('#component-sortable-list');
    var page_slug = $componentList.data('page-slug');

    $componentList.sortable({
        axis: 'y',
        handle: '.handle',
        opacity: 0.75,
        update: function (event, ui) {
            var data = $(this).sortable('serialize');

            console.log(data);

            $.ajax({
                data: data,
                type: 'POST',
                url: '/page/' + page_slug + '/admin/components/order'
            });
        }
    });

    $componentList.disableSelection();
}

function configureAddBoxButtons() {
    $('#add-component-button').off().click(showAddComponentBox);
    $('#cancel-new-component-button, #cancel-new-component-icon').off().click(hideAddComponentBox);

    $('#save-new-component-button').off().click(postNewComponent);
}

function configureItemButtons() {
    $('.edit-component-button').each(function() {
        var $this = $(this);
        $this.off().click({componentId: $this.data('component-id')}, showEditComponent);
    });

    $('.delete-component-button').each(function() {
        var $this = $(this);
        $this.off().click({componentId: $this.data('component-id')}, deleteComponent);
    });
}

function configureEditItemButtons() {
    $('.delete-component-button').each(function() {
        var $this = $(this);
        $this.off().click({componentId: $this.data('component-id')}, deleteComponent);
    });

    $('.save-edit-component-button').each(function() {
        var $this = $(this);
        $this.off().click({componentId: $this.data('component-id')}, saveEditedComponent);
    });

    $('.cancel-edit-component-button').each(function() {
        var $this = $(this);
        $this.off().click({componentId: $this.data('component-id')}, hideEditComponent);
    });
}

function postNewComponent() {
    var $componentName = $('#new-component-name');
    if ($componentName.val() !== "") {
        var $componentList = $('#component-sortable-list');
        var page_slug = $componentList.data('page-slug');

        var postUrl = "/page/" + page_slug + "/admin/components/create";
        var formContents = $('#add-component-form').serialize();

        console.log("Form contents: " + formContents);
        $.ajax({
            type: "POST",
            url: postUrl,
            data: formContents,
            success: insertComponentTemplate
        });
    } else {
        $componentName.parent().addClass('has-error');
        $componentName.on('keyup', function() {
            $(this).off().parent().removeClass('has-error');
        })
    }
}

function saveEditedComponent(event) {
    console.log("Saving edited component " + event.data.componentId);

    var $componentName = $('#edit-component-name-' + event.data.componentId);
    if ($componentName.val() !== "") {
        var $componentList = $('#component-sortable-list');
        var page_slug = $componentList.data('page-slug');

        var postUrl = "/page/" + page_slug + "/admin/components/" + event.data.componentId + "/edit";
        var formContents = $('#edit-component-form-' + event.data.componentId).serialize();

        console.log("Form contents: " + formContents);
        $.ajax({
            type: "POST",
            url: postUrl,
            data: formContents,
            success: function() { hideEditComponent(event) }
        });
    } else {
        $componentName.parent().addClass('has-error');
        $componentName.on('keyup', function() {
            $(this).off().parent().removeClass('has-error');
        })
    }


}

function insertComponentTemplate(renderedData) {
    hideAddComponentBox();
    $('#no-components-notification').addClass('hidden');
    $('#component-sortable-list').append(renderedData);
    initTooltips();
    configureItemButtons();
    initComponentStatusClickSubmit();
}

function removeComponentItem(componentId) {
    $('#item-' + componentId).remove();
    if ($('#component-sortable-list').children().length === 0) {
        $('#no-components-notification').removeClass('hidden');
    }
}

function showAddComponentBox() {
    $('#add-component-list').removeClass('hidden');
    $('#add-component-button').addClass('hidden');
}

function hideAddComponentBox() {
    $('#add-component-list').addClass('hidden');
    $('#new-component-name, #new-component-desc').val("");
    $('#add-component-button').removeClass('hidden');
}

function showEditComponent(event) {
    console.log("Editing component " + event.data.componentId);

    var $componentList = $('#component-sortable-list');
    var page_slug = $componentList.data('page-slug');

    var editUrl = "/page/" + page_slug + "/admin/components/" + event.data.componentId + "/edit";

    $.ajax({
        type: "GET",
        url: editUrl,
        success: function(responseData) {
            console.log("Got edit response data: " + responseData);
            var $itemToReplace = $('#item-' + event.data.componentId);
            $itemToReplace.replaceWith(responseData);
            configureEditItemButtons();
            initTooltips();
        }
    });
}

function hideEditComponent(event) {
    console.log("Canceling edit of component " + event.data.componentId);

    var $componentList = $('#component-sortable-list');
    var page_slug = $componentList.data('page-slug');

    var editUrl = "/page/" + page_slug + "/admin/components/" + event.data.componentId;

    $.ajax({
        type: "GET",
        url: editUrl,
        success: function(responseData) {
            var $itemToReplace = $('#item-' + event.data.componentId);
            $itemToReplace.replaceWith(responseData);
            configureItemButtons();
            initTooltips();
            initComponentStatusClickSubmit();
        }
    });
}

function deleteComponent(event) {
    console.log("Deleting component " + event.data.componentId);
    bootbox.confirm("Delete component?", function (result) {
        if (result === true) {
            var $componentList = $('#component-sortable-list');
            var page_slug = $componentList.data('page-slug');

            var postUrl = "/page/" + page_slug + "/admin/components/" + event.data.componentId + "/delete";

            $.ajax({
                type: "POST",
                url: postUrl,
                success: function() {
                    removeComponentItem(event.data.componentId);
                }
            })
        }
    });
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
