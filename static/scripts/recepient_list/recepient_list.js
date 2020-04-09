$('#add-team').on('click', function () {
        $('.add-team-modal').modal('toggle');
});

$('#add-recepient').on('click', function () {
        $('.add-recepient-modal').modal('toggle');
        $("[name='recepient_name']").prop("required", 'required');

        var url = '/recepient-list/get-team-data/';
        var dropdown_id = $('#team-dropdown');
        var data_val = 'id';
        var data_text = 'team_name';

        _dropdown(url, dropdown_id, data_val, data_text);

});

var url = '/recepient-list/get-team-data/';
var dropdown_id = $('#edit-team-dropdown');
var data_val = 'id';
var data_text = 'team_name';

_dropdown(url, dropdown_id, data_val, data_text);

var recepient_table_id = 'recepient_list';

set_recepient_list(all_data, recepient_table_id);


function _dropdown(_url, dropdown, data_val, data_text){
    // Common dropdown function

    dropdown.empty();

    dropdown.append('<option selected="true" disabled>Choose Team</option>');
    dropdown.prop('selectedIndex', 0);

    var url = _url;

    // Populate dropdown with list of provinces
    $.getJSON(url, function (data) {
      $.each(data, function (key, entry) {
        dropdown.append($('<option></option>').attr('value', entry[data_val]).text(entry[data_text]));
      })
    });
}

function editable_value(id) {
    // This function is for showing editable value into input fields for '.edit-recepient-modal'.

    $.getJSON('/recepient-list/specific-recepient/'+id, function (data) {
      console.log("dattttttttttaaaaaa ========== ", data[0]['name']);
      $('input[name="edit_recepient_name"]').val(data[0]['name']);
      $('input[name="edit_email"]').val(data[0]['email']);
      $('input[name="edit_mobile_no"]').val(data[0]['contact']);
      $('#recepient_edit_submit').val(id);


      var team_id_arr = [];
      for(i=0; i<data[0]['team_id_list'].length; i++){
          console.log("list =========== ", data[0]['team_id_list'][i]);
          if(data[0]['team_id_list'][i] !== ','){
              team_id_arr.push(data[0]['team_id_list'][i]);
          }
      }

      $("select[name='edit_team']").val(team_id_arr).change();

    });
}


$('#team_add_submit').on('click', function () {
    // submit function for team adding

    var data = $('#add-team-form').serializeArray().reduce(function(obj, item) {
    obj[item.name] = item.value;
    return obj;
    }, {});
    console.log('prevous ========================= ', data);
    var crf_token = data['csrfmiddlewaretoken'];

    $.ajax({
        url: '/recepient-list/add-team/',
        type: 'POST',
        dataType: 'json',
        headers:{"X-CSRFToken": crf_token},
        data: data,

        success: function (result) {
            console.log("result =========== ", result);
            location.reload();
            // $('.add-team-modal').modal('toggle');
        }
    });

});

$('#recepient_add_submit').on('click', function () {
    // submit function for recepient adding.

    $('.add-recepient-modal').modal('toggle');
    // console.log("selectedValues ===== ", selectedValues);
    var data = $('#add-recepient-form').serializeArray().reduce(function(obj, item) {

        obj[item.name] = item.value;
        return obj;
    }, {});

    var crf_token = data['csrfmiddlewaretoken'];

    $.ajax({
        url: '/recepient-list/add-recepient/',
        type: 'POST',
        dataType: 'json',
        headers:{"X-CSRFToken": crf_token},
        data: $('#add-recepient-form').serialize(),

        success: function (result) {
            console.log("result =========== ", result);
            location.reload();

        }
    });

});


$('#recepient_edit_submit').on('click', function () {
    // Submit function after recepient editing.

    $('.edit-recepient-modal').modal('toggle');
    var submit_btn_val = $('#recepient_edit_submit').val();
    console.log("submit_btn_val ============ ", submit_btn_val);
    var data = $('#edit-recepient-form').serializeArray().reduce(function(obj, item) {
    if (item.name === 'team'){
        obj[item.name] = team_arr;
    }
    else{
        obj[item.name] = item.value;
    }

    return obj;
    }, {});
    console.log('prevous ========================= ', $('#edit-recepient-form').serialize());
    var crf_token = data['csrfmiddlewaretoken'];

    $.ajax({
        url: '/recepient-list/edit-recepient/'+submit_btn_val+'/',
        type: 'POST',
        dataType: 'json',
        headers:{"X-CSRFToken": crf_token},
        data: $('#edit-recepient-form').serialize(),

        success: function (result) {
            console.log("result =========== ", result);
            location.reload();

        }
    });

});

$('#recepient_delete_submit').on('click', function () {
    // Submit function recepient deleting.

    var submit_del_btn_val = $('#recepient_delete_submit').val();
    console.log("submit_del_btn_val =========== ", submit_del_btn_val);
    var data = $('#delete-recepient-form').serializeArray().reduce(function(obj, item) {
    obj[item.name] = item.value;
    return obj;
    }, {});
    var crf_token = data['csrfmiddlewaretoken'];

    $.ajax({
        url: '/recepient-list/delete-recepient/'+submit_del_btn_val+'/',
        type: 'DELETE',
        dataType: 'json',
        headers:{"X-CSRFToken": crf_token},
        data: {
                user: submit_del_btn_val,
            },

        success: function (result) {
            console.log("result =========== ", result);
            location.reload();

        }
    });
});


function set_recepient_list(all_data, table_id){
    // Recepient list datatable function

         $('#'+table_id).DataTable( {
             "data": all_data,
             "columns": [
            {"data": "name"},
            {"data": "organization"},
            {"data": "email"},
            {"data": "contact"},
            {"data": "team_list"},
            {"data": "date_added"},
             {"data": "id"}
        ],
         "columnDefs": [
            {
                "targets": 6,

                "render": function (data, type, row, meta) {
                    // console.log("row id =========== ", row['id']);
                    return '<button class="recepient-edit-button" value="' + row['id'] + '"><i class=\"fas  fa-user-edit\"></i></button> <button class="recepient-delete-button" value="' + row['id'] + '"><i class=\"fa fa-trash-alt\"></i></button>';
                }
            }
            ],
             "drawCallback": function () {
            $('.recepient-edit-button').on('click', function () {
                $('.edit-recepient-modal').modal('toggle');
                var recepient_id = $(this).val();
                editable_value(recepient_id);

            });

            $('.recepient-delete-button').on('click', function () {
                $('#confirm-recepient-delete').modal('toggle');
                var recepient_id = $(this).val();
                $('#recepient_delete_submit').val(recepient_id);
                console.log("recepient_id =========== ", recepient_id);
            });

        }

         } );
}