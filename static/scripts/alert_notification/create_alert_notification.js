var url = '/recepient-list/get-team-data/';
var dropdown_id = $('#team-dropdown');
var data_val = 'id';
var data_text = 'team_name';

__dropdown(url, dropdown_id, data_val, data_text);

function __dropdown(_url, dropdown, data_val, data_text){
    // Common dropdown function

    dropdown.empty();

    dropdown.append('<option selected="true" disabled>--Select--</option>');
    dropdown.prop('selectedIndex', 0);

    var url = _url;

    // Populate dropdown with list of provinces
    $.getJSON(url, function (data) {
      $.each(data, function (key, entry) {
        dropdown.append($('<option></option>').attr('value', entry[data_val]).text(entry[data_text]));
      })
    });
}

$('#system').on('change', function () {
    $('#send_sms').attr("disabled", true);
});

$('#manual').on('change', function () {
    $('#send_sms').removeAttr("disabled");
});

$('#compose-message-button').on('click', function () {
    // Redirecting '/alert-notification/create-alert-notification/' page

    window.location = '/alert-notification/create-alert-notification/';
});

$('#saved-message-button').on('click', function () {
    //// Redirecting '/alert-notification/saved-message/' page

    window.location = '/alert-notification/saved-message/';
});


$('#send_sms').on('click', function (e) {
    // Changing the action value of the form for sending data directly in 'sms_queue_insert' function of views.py
    // to insert data into 'sms_queue' table

    $('#create-alert-notification-form').attr("action", "/alert-notification/sms-queue/");
});


$('#save_sms').on('click', function () {
    // Changing the action value of the form for sending data directly in 'save_message' function of views.py
    // to insert data into 'alert_sms' table

    $('#create-alert-notification-form').attr("action", "/alert-notification/save-message/");
});

