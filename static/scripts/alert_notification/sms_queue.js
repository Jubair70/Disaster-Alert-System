var recepient_table_id = 'sms_queue_list_table';

set_sms_queue_list(all_data, recepient_table_id);

function set_sms_queue_list(all_data, table_id){
    // SMS Queue list datatable function.

     $('#'+table_id).DataTable( {
         "data": all_data,
         "columns": [
        {"data": "recepint_num_or_email"},
        {"data": "message"},
        {"data": "description"},
        {"data": "message_type"},
        {"data": "status"},
        {"data": "alert_sms_id"}
        ],
         "columnDefs": [],
             "drawCallback": function () {}

         } );
}