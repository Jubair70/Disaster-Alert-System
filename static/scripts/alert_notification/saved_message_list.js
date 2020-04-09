$('#compose-message-button').on('click', function () {
    // Redirecting '/alert-notification/create-alert-notification/' page

    window.location = '/alert-notification/create-alert-notification/';
});

$('#saved-message-button').on('click', function () {
    // Redirecting '/alert-notification/saved-message/' page

    window.location = '/alert-notification/saved-message/';
});

var url = '/recepient-list/get-team-data/';
var dropdown_id = $('#edit-team-dropdown');
var data_val = 'id';
var data_text = 'team_name';

team_dropdown(url, dropdown_id, data_val, data_text);

function team_dropdown(_url, dropdown, data_val, data_text){
    // Common dropdown function

    dropdown.empty();

    // dropdown.append('<option selected="true" disabled>--Select--</option>');
    dropdown.prop('selectedIndex', 0);

    var url = _url;

    // Populate dropdown with list of provinces
    $.getJSON(url, function (data) {
      $.each(data, function (key, entry) {
        dropdown.append($('<option></option>').attr('value', entry[data_val]).text(entry[data_text]));
      })
    });
}

function message_editable_value(id) {

    // This function is for showing editable value into input fields for '#edit-message-modal'.

    $('#message_edit_submit').val(id);

    $.getJSON('/alert-notification/specific-message/'+id, function (data) {
      if(data[0]['message_type'] === 'email'){
          $('input[id="email"]').attr('checked', true);
      }
      else if(data[0]['message_type'] === 'sms'){
          $('input[id="sms"]').attr('checked', true);
      }
      else{
          $('input[id="email"]').attr('checked', false);
          $('input[id="sms"]').attr('checked', false);
      }

      if(data[0]['process_type'] === 'system'){
          $('input[id="edit_system"]').attr('checked', true);
      }
      else if(data[0]['process_type'] === 'manual'){
          $('input[id="edit_manual"]').attr('checked', true);
      }
      else{
          $('input[id="edit_system"]').attr('checked', false);
          $('input[id="edit_manual"]').attr('checked', false);
      }

      if(data[0]['disaster_type'] === 'cyclone'){
          $('input[id="cyclone"]').attr('checked', true);
      }
      else if(data[0]['disaster_type'] === 'flood'){
          $('input[id="flood"]').attr('checked', true);
      }
      else{
          $('input[id="cyclone"]').attr('checked', false);
          $('input[id="flood"]').attr('checked', false);
      }

      var i;
      var team_id_arr = [];

      for(i=0; i<data[0]['team_id_list'].length; i++){
          if(data[0]['team_id_list'][i] !== ','){
              team_id_arr.push(data[0]['team_id_list'][i]);
          }
      }

      $('input[name="edit_message"]').val(data[0]['text']);
      $('input[name="edit_message_details"]').val(data[0]['description']);
      $("select[name='edit-team-select']").val(team_id_arr).change();
      $("select[name='edit_stage_id']").val(data[0]['stage_id']).change();
    });
}

$('#message_edit_submit').on('click', function () {
    // Submit function for edited message

    $('.edit-message-modal').modal('toggle');
    var submit_btn_val = $('#message_edit_submit').val();
    console.log("submit_btn_val ============ ", submit_btn_val);
    var data = $('#edit-recepient-form').serializeArray().reduce(function(obj, item) {
        obj[item.name] = team_arr;
    return obj;
    }, {});
    var crf_token = data['csrfmiddlewaretoken'];

    $.ajax({
        url: '/alert-notification/edit-message/'+submit_btn_val+'/',
        type: 'POST',
        dataType: 'json',
        headers:{"X-CSRFToken": crf_token},
        data: $('#edit-message-form').serialize(),

        success: function (result) {
            console.log("result =========== ", result);
            location.reload();

        }
    });
});

function send_message(id){
    // sending save message table data to server for submiting with the send icon.

    $.getJSON('/alert-notification/specific-message/'+id, function (data) {
        var all_data = {};
      all_data['message'] = data[0]['text'];
      all_data['message_details'] = data[0]['description'];
      all_data['message_type'] = data[0]['message_type'];
      all_data['team-select'] = data[0]['team_id_list'];
      all_data['iddd'] = id;

      $.ajax({
        url: '/alert-notification/sms-queue/',
        type: 'POST',
        data: all_data,

        success: function (result) {
            console.log("result ======== ", result);
            location.reload();
        }
    });
    });
}

var recepient_table_id = 'saved_message_list';

set_saved_message_list(all_data, recepient_table_id);

function set_saved_message_list(all_data, table_id){
    // Saved message list datatable function.

     $('#'+table_id).DataTable( {
         "data": all_data,
         "columns": [
        {"data": "id"},
        {"data": "text"},
        {"data": "description"},
        {"data": "created_on"},
        {"data": "team_list"},
        {"data": "stage_id"},
         {"data": "message_type"},
         {"data": "rec_id_count"},
         {"data": "id"}
        ],
         "columnDefs": [
            {
                "targets": 8,

                "render": function (data, type, row, meta) {
                    // console.log("row id =========== ", row['id']);
                    // return '<button class="recepient-edit-button" value="' + row['id'] + '"><i class=\"fas  fa-user-edit\"></i></button> <button class="recepient-delete-button" value="' + row['id'] + '"><i class=\"fa fa-trash-alt\"></i></button>';
                    var send_btn = "";
                    if(row['is_sent_or_saved']  !== 1){
                        send_btn = "       ";
                    }
                    if(row['process_type']  === 'system'){
                        send_btn = "       ";
                    }
                    else {
                        send_btn = "<a class=\"send-message\" href=\"#\" data-href='"+row['id']+"'><i class=\"fas fa-paper-plane\"></i></a>  ";
                    }
                    let button = send_btn + "<a class=\"edit-message\" href=\"#\" data-toggle=\"modal\" data-target=\"#edit-message-modal\" data-href='"+row['id']+"'><i class=\"fas  fa-user-edit\"></i></a> <a class=\"delete-saved-message\" href=\"#\" data-toggle=\"modal\" data-target=\"#confirm-saved-message-delete\" data-href='/alert-notification/saved-message-delete/" +row['id']+ "'><i class=\"fa fa-trash-alt\"></i></a>";
                    return button;
                }
            }
            ],
             "drawCallback": function () {
                 $('.send-message').on('click', function (e) {
                    var r_id = $(this).attr("data-href");
                    send_message(r_id);
                    });

                $('.edit-message').on('click', function (e) {
                    var row_id = $(this).attr("data-href");
                    message_editable_value(row_id);
                    });

                $('.delete-saved-message').on('click', function (e) {
                    var del_url = $(this).attr("data-href");
                    $('#saved_message_delete_submit').attr("href", del_url);
                    });

            }

     });
}