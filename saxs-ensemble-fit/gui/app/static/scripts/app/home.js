var pages, filterOptions = {}, compBeingDeleted;

$(function () {
    setSliderValue();
    changeSliderValue();
    setOptParamsVisibility(0);
    setDefaultCalcStepsValue('random_walk');
    changeDefaultCalcStepsValueOnCalcTypeChange();
    highlightSelectedRadioButton();
    fileUploadButtonsBehaviour();
    advancedSettingsToggleClick();
    clearFilenamesAfterFormReset();

    reloadList();
    changeStatusColor();
    nonErroneousComputationRowHoverAndClick();
    erroneousComputationRowHoverAndClick();
//    deleteAllHoverAndClick();
    deleteRowButtonHoverAndClick();

    setPages();
    changePageOnPageClick();
    changePageOnNextClick();
    changePageOnPreviousClick();

    filterToggleClick();
    sortList();
    filterList();
    clearFilter();

    validation();
    fileFormatValidation();

    tooltips();
    dialog();
});

//---------------------------------------------------------------------------------ajax callback functions---------------------------------------------------------------------------------------
//success function for asynchronous calls, erases current list of computations and replaces it with new list
function onGetExperimentsSuccess(data) {
    $('.experiment_list .experiment_row').detach();
    var comps = data.comps;
    pages = data.pages;

    for (var i = 0; i < comps.length; i++) {
        var newEl = "<div class=\"experiment_row " + comps[i].status + "\">";

        if(comps[i].progress != 0 || comps[i].status == 'user_error' || comps[i].status == 'server_error'){
            newEl += "<a href=\"/view_experiment/" + comps[i].user_id + "/" + comps[i].comp_guid + "\"></a>";
        }

        newEl += "<span class=\"date\">" + comps[i].date + "</span>";
        newEl += "<span class=\"name\">" + comps[i].name + "</span>";
        newEl += "<span class=\"progress\">" + comps[i].progress + "</span>";
        newEl += "<span class=\"status\">" + comps[i].status + "</span>";
        if(comps[i].progress != 0 || comps[i].status == 'user_error' || comps[i].status == 'server_error'){
            newEl += "<img class='delete' src=\"/static/styles/icons/recycle_bin.png\">";
        }
        if(comps[i].status == "user_error"){
            newEl += "<div class=\"error-row\">" + comps[i].error_message + "</div></div>";
        }
        $('.experiments-rows-wrapper').append(newEl);
    }
    changeStatusColor();
    nonErroneousComputationRowHoverAndClick();
    erroneousComputationRowHoverAndClick();
//    deleteAllHoverAndClick();
    deleteRowButtonHoverAndClick();
}

//error function for getComputations asynchronous calls, tries to log error to saxs.log on server
function onGetComputationsError(jqXHR, textStatus, errorThrown) {
    $('.get-comps-error').show();
    setTimeout(function () {
        $('.error-info').fadeOut(700);
        hideOverlays();
    }, 3000);
}

//error function for deleteComputation asynchronous call, tries to log error to saxs.log on server
function onDeleteComputationError(jqXHR, textStatus, errorThrown) {
    $('.delete-comps-error').show();
    setTimeout(function () {
        $('.error-info').fadeOut(700);
        hideOverlays();
    }, 3000);
}

//complete function for asynchronous calls, hides loading gif and displays error message to user
function onGetExperimentsComplete(textStatus) {
    setTimeout(function(){
        $('.experiment_list_overlay').hide();
        if (textStatus.status == 200)
            hideOverlays();
    }, 300);
}
//--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//---------------------------------------------------------------------------------form manipulation------------------------------------------------------------------------------------------
function setSliderValue(){
    $('.qRange-value').text($('#qRange').val());
}

function changeSliderValue(){
    $('#qRange').on('mousemove mouseup', function(){
        $('.qRange-value').text($(this).val());
    });
}

function changeDefaultCalcStepsValueOnCalcTypeChange(){
    $('input[name=calcType]').on('change', function(){
        highlightSelectedRadioButton();
        var value = $('input[name=calcType]:checked').val();
        setDefaultCalcStepsValue(value);

        if (value == 'random_walk') {
            setOptParamsVisibility(0);
        } else {
            setOptParamsVisibility(1);
        }
    });
}

function setDefaultCalcStepsValue(value){
    if (value == 'random_walk')
        $('#calcSteps').val(500);
    else
        $('#calcSteps').val(10000);
}

function setOptParamsVisibility(visible){
    if (visible == 0)
        $('#alpha, #beta, #gamma').attr('disabled', true).css('color', '#a8a8a8').prev().css('color', '#a8a8a8');
    else
        $('#alpha, #beta, #gamma').attr('disabled', false).css('color', '#4c4c4c').prev().css('color', '#4c4c4c');
}

function highlightSelectedRadioButton(){
    $('span.calcType label').removeClass('selected-radio-button');
    $('input[name=calcType]:checked').next().addClass('selected-radio-button');
}

function clearFilenamesAfterFormReset(){
    $('#btnReset').on('click', function(){
        $('.row-models span.filename').text("");
        $('.row-expData span.filename').text("");
    });
}

function fileUploadButtonsBehaviour(){
    $('#models').on('change', function(){
        $(this).parent().next().text(modifyFilename($(this).val()));
    });
    $('#expData').on('change', function(){
        $(this).parent().next().text(modifyFilename($(this).val()));
    });
}

function advancedSettingsToggleClick(){
    $('.advanced-settings-toggle-content-wrapper').on('click', function(){
        $('.advanced-settings').slideToggle(150);
        $(this).find('div.img').toggleClass('advanced-settings-toggle-clicked');
    });
}
//--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------list of computations manipulation---------------------------------------------------------------------------------
//this function reloads list with computations - it asynchronously calls server method that returns list of computations in JSON
function reloadList(){
    $('.img_reload_list').on('click', function(){
        $('.error-info').hide();
        showOverlays();
        $('.search-filter input').val('');
        filterOptions = {};
        $.ajax({
            type: 'POST',
            url: "/get_experiments/0/date/-1",
            data: JSON.stringify({}),
            contentType: 'application/json',
            success: function(data){
                onGetExperimentsSuccess(data);
                createPaginationControls(pages);
                setPages();
                resetSortOrder();
            },
            complete: onGetExperimentsComplete,
            error: onGetComputationsError
        })
    });
}

function changeStatusColor() {
    $('.experiment_row span.status').each(function () {
        switch ($(this).text()) {
            case "accepted":
                $(this).css('color', '#b2a300');
                break;
            case "done":
                $(this).css('color', 'green');
                break;
            case "running":
                $(this).css('color', 'lightskyblue');
                break;
            case "queued":
                $(this).css('color', 'blue');
                break;
            case "checked":
                $(this).css('color', 'brown');
                break;
            case "preprocessed":
                $(this).css('color', 'pink');
                break;
            case "storage_ready":
                $(this).css('color', 'purple');
                break;
            case "optim_completed":
                $(this).css('color', 'magenta');
                break;
            case "server_error":
                $(this).css('color', 'red');
                break;
            case "user_error":
                $(this).css('color', 'red');
                break;
            default:
                break;
        }
    });
}

//hovering effect over a row with a computation. Clicking on a row will sent player to a page with results of a clicked computation
function nonErroneousComputationRowHoverAndClick(){
    $('.experiment_row:not(.server_error, .user_error)').on('mouseover', function () {
        if ($(this).find('a').length != 0) {
            $(this).addClass('highlight');
            $(this).find('img').css('opacity', '1');
        }
    }).on('mouseout', function () {
        if ($(this).find('a').length != 0) {
            $(this).removeClass('highlight');
            $('.experiment_row img').css('opacity', '0');
        }
    }).on('click', function () {
        if ($(this).find('a').length != 0) {
            window.location.href = $(this).children('a').attr('href');
        }
    });
}

//hovering effect over a row with an erroneous computation. Clicking on this row will display player an error message
function erroneousComputationRowHoverAndClick(){
    $('.experiment_row.user_error, .experiment_row.server_error').on('mouseover', function () {
        $(this).addClass('highlight');
        $(this).find('img').css('opacity', '1');
    }).on('mouseout', function () {
        $(this).removeClass('highlight');
        $('.experiment_row img').css('opacity', '0');
    }).on('click', function () {
        var errorRow = $(this).children('.error-row');
        errorRow.slideToggle(150);
        if(errorRow.length == 1)
            $(this).toggleClass("selectedRow");
    });
}

//function deleteAllHoverAndClick(){
//    $('.list-header .delete-all').on('mouseover', function () {
//        $(this).attr('src', '/static/styles/icons/recycle_bin_red.png');
//    }).on('mouseout', function () {
//        $(this).attr('src', '/static/styles/icons/recycle_bin.png');
//    }).on('click', function () {
//        alert("Are you sure you want to delete all computations ?");
//        $.ajax({
//            type: 'POST',
//            url: "/delete_computations",
//            data: JSON.stringify({'all': 'True'}),
//            contentType: 'application/json',
//            success: function(){
//                $('.img_reload_list').trigger('click');
//            }
//        });
//    });
//}

function deleteRowButtonHoverAndClick(){
    $('.experiment_row img').on('mouseover', function () {
        $(this).attr('src', '/static/styles/icons/recycle_bin_red.png');
    }).on('mouseout', function () {
        $(this).attr('src', '/static/styles/icons/recycle_bin.png');
    }).on('click', function (e) {
        e.stopPropagation();
        compBeingDeleted = getInfoOfComputationBeingDeleted($(this).parent());
        $('.delete-dialog').dialog("open");
    });
}

function deleteComputation(){
    $('.error-info').hide();
    showOverlays();
    var data = compBeingDeleted;
    data['filter_values'] = filterOptions;

    var selectedPageEl = $('span.page.selectedPaginationControl');
    if (selectedPageEl.length == 0)
        var selectedPage = 0;
    else
        selectedPage = parseInt(selectedPageEl.text()) - 1;

    $.ajax({
        type: 'POST',
        url: "/delete_computations/" + selectedPage + "/" + getSortOption() + "/" + determineSortOrder(),
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(data){
            onGetExperimentsSuccess(data);
            createPaginationControls(pages);
            setPages();
            selectPageControl(selectedPage + 1);
        },
        complete: onGetExperimentsComplete,
        error: onDeleteComputationError
    });
}

function getInfoOfComputationBeingDeleted(element){
    var json = {'all': 'False'};
    json['comp_guid'] = element.children('a').attr('href').split('/')[3];
    return json;
}

function hideOverlays() {
    $('.list-header-overlay').hide();
    $('.search-filter-overlay').hide();
    $('.img-reload-list-overlay').hide();
    $('.filter-toggle-overlay').hide();
    $('.pagination-controls-overlay').hide();
}

function showOverlays() {
    $('.experiment_list_overlay').show();
    $('.list-header-overlay').show();
    $('.search-filter-overlay').show();
    $('.img-reload-list-overlay').show();
    $('.filter-toggle-overlay').show();
    $('.pagination-controls-overlay').show();
}
//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------pagination controls-------------------------------------------------------------------------------------------
//this function displays computations for clicked page
function changePageOnPageClick(){
    $('.pagination-controls').on('click', 'span.page:not(.previous, .next, .selectedPaginationControl)', function(){
        var selectedPage = $(this);
        $('.error-info').hide();
        showOverlays();
        $.ajax({
            type: 'POST',
            url: "/get_experiments/" + (parseInt($(this).text()) - 1).toString() + "/" + getSortOption() + "/" + determineSortOrder(),
            contentType: 'application/json',
            success: function (data) {
                onGetExperimentsSuccess(data);
                selectPageControl(selectedPage.text());
            },
            complete: onGetExperimentsComplete,
            error: onGetComputationsError,
            data: JSON.stringify(filterOptions),
            dataType: 'json'
        });
    });
}

//this function displays computation for selected page when user clicked 'next' button
function changePageOnNextClick(){
    $('span.next').on('click', function(){
        var selectedPage = $('span.page.selectedPaginationControl');
        var lastVisiblePage = $('span.page:not(.previous, .next):visible').last();
        if ( !selectedPage.is($('span.page:not(.previous, .next)').last()) ){
            $('.error-info').hide();
            showOverlays();
            $.ajax({
                type: 'POST',
                url: "/get_experiments/" + selectedPage.text() + "/" + getSortOption() + "/" + determineSortOrder(),
                contentType: 'application/json',
                success: function (data) {
                    onGetExperimentsSuccess(data);
                    selectPageControl(parseInt(selectedPage.text()) + 1);
                    if (selectedPage.is(lastVisiblePage)) {
                        $('span.page:not(.previous, .next):visible').first().addClass('hiddenBefore');
                        $('span.page:not(.previous, .next).hiddenAfter').first().removeClass('hiddenAfter');
                    }
                },
                complete: onGetExperimentsComplete,
                error: onGetComputationsError,
                data: JSON.stringify(filterOptions),
                dataType: 'json'
            });
        }
    });
}

//this function displays computation for selected page when user clicked 'previous' button
function changePageOnPreviousClick(){
    $('span.previous').on('click', function(){
        var selectedPage = $('span.page.selectedPaginationControl');
        var firstVisiblePage = $('span.page:not(.previous, .next):visible').first();
        if ( selectedPage.text() != "1" ){
            $('.error-info').hide();
            showOverlays();
            $.ajax({
                type: 'POST',
                url: "/get_experiments/" + ((parseInt(selectedPage.text()) - 2)).toString() + "/" + getSortOption() + "/" + determineSortOrder(),
                contentType: 'application/json',
                success: function (data) {
                    onGetExperimentsSuccess(data);
                    selectPageControl(parseInt(selectedPage.text()) - 1);
                    if (selectedPage.is(firstVisiblePage)) {
                        $('span.page:not(.previous, .next).hiddenBefore').last().removeClass('hiddenBefore');
                        $('span.page:not(.previous, .next):visible').last().addClass('hiddenAfter');
                    }
                },
                complete: onGetExperimentsComplete,
                error: onGetComputationsError,
                data: JSON.stringify(filterOptions),
                dataType: 'json'
            });
        }
    });
}

function createPaginationControls(pages){
    $('.pagination-controls span').detach();
    if (pages <= 1)
        return;
    $('.pagination-controls').append("<span class=\"page previous\"> < </span>");
    var newEl;
    for (var i = 1; i <= parseInt(pages); i++){
        newEl = "<span class=\"page _" + i + "\">" + i + "</span>";
        $('.pagination-controls').append(newEl);
    }
    $('.pagination-controls').append("<span class=\"page next\"> > </span>");
    changePageOnNextClick();
    changePageOnPreviousClick();
    changePageOnPageClick();
}

function setPages(){
    $('span._1').addClass('selectedPaginationControl');
    $('span.page:not(.previous, .next)').slice(13).addClass('hiddenAfter');
}

//this function highlights selected page
function selectPageControl(page){
    $('span.page').each(function(){
        $(this).removeClass('selectedPaginationControl');
    });
    if ($('span.page:not(.previous, .next)').length != 0 && parseInt($('span.page:not(.previous, .next)').last().text()) < page)
        $('span._' + (page - 1)).addClass('selectedPaginationControl');
    else
        $('span._' + page).addClass('selectedPaginationControl');
}
//-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------filtering and sorting----------------------------------------------------------------------------------
function filterToggleClick(){
    $('.experiment_list .filter-toggle').on('click', function(){
        $('.experiment_list .search-filter').slideToggle(150);
        $(this).toggleClass('filter-toggle-clicked');
    });
}

function filterList(){
    $('.search-filter .filter').on('click', function(){
        if (!filterValidation()) return;
        $('.search-filter input').removeClass("search-filter-validation-error");
        filterOptions = {};
        $('.error-info').hide();
        showOverlays();
        $.ajax({
            type: 'POST',
            url: "/get_experiments/0/" + getSortOption() + '/' + determineSortOrder(),
            contentType: 'application/json',
            success: function(data){
                onGetExperimentsSuccess(data);
                createPaginationControls(pages);
                setPages();
            },
            complete: onGetExperimentsComplete,
            error: onGetComputationsError,
            data: JSON.stringify(getFilterArguments()),
            dataType: 'json'
        });
    });
}

function sortList(){
    $('.list-header > span > span').on('click', function(){
        var clickedEl = $(this);
        setSortOrder(clickedEl.parent());
        $('.error-info').hide();
        showOverlays();
        $.ajax({
            type: 'POST',
            url: "/get_experiments/0/" + $(this).parent().attr('id') + "/" + determineSortOrder(),
            contentType: 'application/json',
            success: function (data) {
                onGetExperimentsSuccess(data);
                selectPageControl(1);
                showSortOrderIcon(clickedEl);
            },
            complete: onGetExperimentsComplete,
            error: onGetComputationsError,
            data: JSON.stringify(filterOptions),
            dataType: 'json'
        });
    });
}

function clearFilter() {
    $('.search-filter .clear-filter').on('click', function(){
        $('.search-filter input').val("").removeClass("search-filter-validation-error");
    });
}

function showSortOrderIcon(clickedElement){
    $('.list-header span img').removeClass('visible');
    clickedElement.children('img').addClass('visible');
    if (determineSortOrder() == 1)
        clickedElement.children('img').attr('src', '/static/styles/icons/arrow_up.png');
    else
        clickedElement.children('img').attr('src', '/static/styles/icons/arrow_down2.png');
}

function setSortOrder(element){
    if(element.hasClass('ascending'))
        element.removeClass('ascending').addClass('descending');
    else if(element.hasClass('descending'))
        element.removeClass('descending').addClass('ascending');
    else {
        $('.list-header span').removeClass();
        element.addClass('descending');
    }
}

function determineSortOrder(){
    var sortAttr = $('.list-header span.ascending, .list-header span.descending');
    if (sortAttr.length != 0 && sortAttr.hasClass('ascending'))
        return 1;
    if (sortAttr.length != 0 && sortAttr.hasClass('descending'))
        return -1;
    return 0;
}

function getSortOption(){
    var sortAttr = $('.list-header span.ascending, .list-header span.descending');
    if (sortAttr.length == 0)
        return 0;
    return sortAttr.attr('id');
}

function resetSortOrder(){
    $('.list-header span').removeClass();
    $('.list-header span#date').addClass('descending');
    $('.list-header span img').removeClass('visible');
    $('.list-header span#date img').attr('src', '/static/styles/icons/arrow_down2.png').addClass('visible');
}

function getFilterArguments(){
    var result = {};
    $('.search-filter input').each(function(){
        if($(this).val().trim() != "") {
            result[$(this).attr('class')] = $(this).val().trim();
            filterOptions[$(this).attr('class')] = $(this).val().trim();
        }$('.search-filter input.progress')
    });
    return result;
}
//-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//----------------------------------------------------------------------------------validation-----------------------------------------------------------------------------------------
function validation() {
    $('#new_experiment_form').validate({
        rules: {
            title: {
                required: true
            },
            qRange: {
                required: true,
                number: true
            },
            calcSteps: {
                required: true,
                range: [500, 1000000],
                number: true
            },
            stepsBetweenSync: {
                range: [100, 10000],
                number: true
            },
            alpha: {
                number: true
            },
            beta: {
                number: true
            },
            gamma: {
                number: true
            }
        },
        errorPlacement: function(error, element) {
            return true;
        }
    });
}

//jquery validation plugin does not validate allowed extension for some reason mysterious to me
//this method validates selected file for models
//it validates file on form submit and when any input(textarea) control in a form recevies a focus(to simulate jquery validation plugin extension behaviour of validating forms
//when user types in a value and then clicks on a different input control )
function fileFormatValidation() {
    $('form textarea').on('focus', function(){
        if ($('#models').val() != "")
            validateFileFormatForModels();
        if ($('#expData').val() != "")
            validateFileFormatForExpData();
    });
    $('form input').not('input[type=submit]').not('input[type=reset]').on('focus', function(){
        if ($('#models').val() != "")
            validateFileFormatForModels();
        if ($('#expData').val() != "")
            validateFileFormatForExpData();
    });
    $('#new_experiment_form').on('submit', function(){
        var bool1 = validateFileFormatForModels();
        var bool2 = validateFileFormatForExpData();
        if (!bool1 || !bool2)
            return false;
    });
}

function validateFileFormatForModels(){
    var allowedExtensions = ["zip", "tar.gz", "pdb", "rar", "tar.bz2"];
    var firstDot = $('#models').val().indexOf('.');
    if (firstDot != -1) {
        var extension = $('#models').val().substring(firstDot + 1);
        if(allowedExtensions.indexOf(extension) == -1) {
            $('#models').parent().next().addClass('file-extension-validation-error');
            return false;
        } else {
            $('#models').parent().next().removeClass('file-extension-validation-error');
            return true;
        }
    }
    $('#models').parent().next().addClass('file-extension-validation-error');
    return false;
}

function validateFileFormatForExpData(){
    var allowedExtensions = ["dat"];
    var expDataInput = $('#expData');
    var firstDot = expDataInput.val().indexOf('.');
    if (firstDot != -1) {
        var extension = expDataInput.val().substring(firstDot + 1);
        if(allowedExtensions.indexOf(extension) == -1) {
            expDataInput.parent().next().addClass('file-extension-validation-error');
            return false;
        } else {
            expDataInput.parent().next().removeClass('file-extension-validation-error');
            return true;
        }
    }
    expDataInput.parent().next().addClass('file-extension-validation-error');
    return false;
}

function filterValidation(){
    var isValid = true;

    var progressInput = $('.search-filter input.progress');
    var progressRegEx1 = /^\s*[><=]\s\d+\s*$/;
    var progressRegEx2 = /^\s*[><]=\s\d+\s*$/;
    var progressRegEx3 = /^\s*\d+\s-\s\d+\s*$/;
    if (!(progressRegEx1.test(progressInput.val()) || progressRegEx2.test(progressInput.val()) || progressRegEx3.test(progressInput.val()) || progressInput.val() == "")) {
        progressInput.addClass('search-filter-validation-error');
        isValid = isValid && false;
    }

    var dateInput = $('.search-filter input.date');
    var dateRegEx1 = /^\s*[><=]\s\d{1,2}\/\d{1,2}\/\d{4}\s*$/;
    var dateRegEx2 = /^\s*[><]=\s\d{1,2}\/\d{1,2}\/\d{4}\s*$/;
    var dateRegEx3 = /^\s*\d{1,2}\/\d{1,2}\/\d{4}\s-\s\d{1,2}\/\d{1,2}\/\d{4}\s*$/;
    if (!(dateRegEx1.test(dateInput.val()) || dateRegEx2.test(dateInput.val()) || dateRegEx3.test(dateInput.val()) || dateInput.val() == "")) {
        dateInput.addClass('search-filter-validation-error');
        isValid = isValid && false;
    }

    var statusInput = $('.search-filter input.status');
    var statusRegEx = /^\s*(\w[ ]?)+\s*$/;;
    if (!(statusRegEx.test(statusInput.val()) || statusInput.val() == "")) {
        statusInput.addClass('search-filter-validation-error');
        isValid = isValid && false;
    }

    var nameInput = $('.search-filter input.name');
    var nameRegEx = /.*/;
    if (!(nameRegEx.test(nameInput.val()))) {
        nameInput.addClass('search-filter-validation-error');
        isValid = isValid && false;
    }

    return isValid;
}
//-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
function dialog(){
    $( ".delete-dialog" ).dialog({
        title: "Are you sure ?",
        draggable: false,
        autoOpen: false,
        resizable: false,
        height:140,
        modal: true,
        position: { my: 'center', at: 'top-70 center'},
        buttons: {
            "Yes": function() {
                $( this ).dialog( "close" );
                deleteComputation();
            },
            "Cancel": function() {
                $( this ).dialog( "close" );
                compBeingDeleted = {};
            }
        }
    });
}

function tooltips() {
    var formFieldPosition = {
        my: "left center",
        at: "right+20 center",
        collision: "none"
    };
    var filterFieldPosition = {
        my: "center top+40",
        at: "center",
        collision: "none"
    };
    $('input.date').tooltip({
        content: "doplnit napovedu k filtrovaniufvgsdtbdsgdbgbvsgfbvgf bsgbsg b gb r r  rggg rvbr  rgrgvrggvr rvrvv vrv vrgfv lfkdnmnvflk fklmvvkm fgk gk glrgk rfgklv   rlkvrklvvlkm lkgdvklr gkvrkl lfkemrfkl",
        position: filterFieldPosition,
        items: "input.date",
        tooltipClass: "upArrowTooltip"
    });
    $('input.status').tooltip({
        content: "doplnit napovedu k filtrovaniu",
        position: filterFieldPosition,
        items: "input.status",
        tooltipClass: "upArrowTooltip"
    });
    $('input.name').tooltip({
        content: "doplnit napovedu k filtrovaniu",
        position: filterFieldPosition,
        items: "input.name",
        tooltipClass: "upArrowTooltip"
    });
    $('input.progress').tooltip({
        content: "doplnit napovedu k filtrovaniu",
        position: filterFieldPosition,
        items: "input.progress",
        tooltipClass: "upArrowTooltip"
    });
    $('.delete-all').tooltip({
        content: "Delete all",
        position: {
            my: "right",
            at: "left-20",
            collision: "none"
        },
        items: ".delete-all",
        tooltipClass: "rightArrowTooltip"
    });
    $('.delete').tooltip({
        content: "Delete",
        position: {
            my: "right",
            at: "left-20",
            collision: "none"
        },
        items: ".delete",
        tooltipClass: "rightArrowTooltip"
    });
    $('.filter-toggle').tooltip({
        content: "Search filter",
        position: {
            my: "right",
            at: "left-20",
            collision: "none"
        },
        items: ".filter-toggle",
        tooltipClass: "rightArrowTooltip"
    });
    $( ".img_reload_list" ).tooltip({
        content: "Reload list",
        position: formFieldPosition,
        items: ".img_reload_list",
        tooltipClass: "leftArrowTooltip",
    });
    $( ".row-models" ).tooltip({
        content: "Allowed file formats: 'pdb'.",
        position: formFieldPosition,
        items: ".row-models",
        tooltipClass: "leftArrowTooltip"
    });
    $( ".row-expData" ).tooltip({
        content: "Allowed file formats: 'dat'.",
        position: formFieldPosition,
        items: ".row-expData",
        tooltipClass: "leftArrowTooltip"
    });
    $( "#calcSteps" ).tooltip({
        content: "Integer number between 500 - 1 000 000.",
        position: formFieldPosition,
        items: "#calcSteps",
        tooltipClass: "leftArrowTooltip"
    });
    $( "#stepsBetweenSync" ).tooltip({
        content: "Integer number between 100 - 10 000.",
        position: formFieldPosition,
        items: "#stepsBetweenSync",
        tooltipClass: "leftArrowTooltip"
    });
    $( "#alpha" ).tooltip({
        content: "Maximal length of random walk step, 1 is whole range. Float number.",
        position: formFieldPosition,
        items: "#alpha",
        tooltipClass: "leftArrowTooltip"
    });
    $( "#beta" ).tooltip({
        content: "This increase of chi2 is accepted with 10% probability by Metropolis criterion. Float number.",
        position: formFieldPosition,
        items: "#beta",
        tooltipClass: "leftArrowTooltip"
    });
    $( "#gamma" ).tooltip({
        content: "chi2 difference scaling in stochastic tunneling transformation. Float number.",
        position: formFieldPosition,
        items: "#gamma",
        tooltipClass: "leftArrowTooltip"
    });
}

//this function modifies name of the selected file to show only filename
function modifyFilename(filename){
    var index = filename.indexOf("fakepath");
    if (index == -1)
        return filename;
    return filename.substring(index + 9);
}


