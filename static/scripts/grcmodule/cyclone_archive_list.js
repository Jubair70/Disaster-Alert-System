
    $(function () {
//         $('[data-toggle="tooltip"]').tooltip()
    $('#from_date').datepicker({
                endDate: '0d',
                format: 'yyyy-mm-dd',
                todayHighlight: true
            }).on('changeDate', function () {
                $(this).datepicker('hide');
            });

            $('#to_date').datepicker({
                endDate: '0d',
                format: 'yyyy-mm-dd',
                todayHighlight: true
            }).on('changeDate', function () {
                $(this).datepicker('hide');
            });
        });

        var dateObj = moment();
        var prevDateObj = moment().subtract(30, 'd');
        console.log(dateObj,prevDateObj);
        $('#from_date').val(dateObj.format('YYYY-MM-DD'));
        $('#to_date').val(dateObj.format('YYYY-MM-DD'));




            var table = $('#all_info_table').DataTable({
//                "scrollX": true,
                "ordering": false,
//                deferRender: true,
                pagination:false,
                scrollCollapse: true
//                ,
//                fixedColumns:   {
//                    leftColumns: 1,
//                    rightColumns: 1
//                }
            });





        $('.delete-item').on('click', function (e) {
            var criteria_id = $(this).attr("data-href");
            $('.btn-ok').attr("href", criteria_id);
        });

        if ($('.alert-block').is(':visible')) {
            window.setTimeout(function () {
                $(".alert-success").fadeTo(1500, 0).slideUp(500, function () {
                    $(this).remove();
                });
            }, 5000);
        }


            $('#generate_report').on('click', function (e) {

               table.destroy();


                var from_date   = $('#from_date').val();
                var to_date     = $('#to_date').val();


                $.ajax({
                    url: '/modules/get_cyclone_archive_list/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        'from_date':from_date
                        ,'to_date':to_date

                    },
                    beforeSend: function () {

                    },


                    success: function (list) {
                            var tbody = '';
                        for (var idx in list) {
                        if(list[idx].file_type == 'png' || list[idx].file_type == 'jpg')
                            tbody += '<tr><td>' + list[idx].file_source + '</td><td>' + list[idx].file_name +'</td><td>'+list[idx].file_type+'</td><td>' + list[idx].added_on +'</td><td>' + list[idx].added_by +'</td><td class="td-center"><a class="tooltips" style="margin-left:10px; cursor:pointer;" data-container="body"  data-placement="top" onclick = "load_img(\''+list[idx].file_location+'\')" title="View" ><i class="fas fa-image"></i></i></a><a class="tooltips" style="margin-left:10px" data-container="body"  data-placement="top" href="'+list[idx].file_location+'" title="Download" download ><i class="fas fa-download"></i></i></a><a class="delete-item tooltips"  style="margin-left:10px" data-placement="top" data-toggle="modal"  data-target="#confirm-delete" title="Delete" href="#" data-href="/modules/delete_cyclone_archive_files/' + list[idx].id +'/' + list[idx].archive_type +'/"><i class="fa fa-trash-alt"></i></a></td></tr>';
                        else tbody += '<tr><td>' + list[idx].file_source + '</td><td>' + list[idx].file_name +'</td><td>'+list[idx].file_type+'</td><td>' + list[idx].added_on +'</td><td>' + list[idx].added_by +'</td><td class="td-center"><a class="tooltips" style="margin-left:10px" data-container="body"  data-placement="top" href="'+list[idx].file_location+'" title="Download" download ><i class="fas fa-download"></i></i></a><a class="delete-item tooltips"  style="margin-left:10px" data-placement="top" data-toggle="modal"  data-target="#confirm-delete" title="Delete" href="#" data-href="/modules/delete_cyclone_archive_files/' + list[idx].id +'/' + list[idx].archive_type +'/"><i class="fa fa-trash-alt"></i></a></td></tr>';
                        }
                        $("#all_info_table").find('tbody').html(tbody);
                       table = datatable_reinitialize();
                         $('.delete-item').on('click', function (e) {
                        var criteria_id = $(this).attr("data-href");
                        $('.btn-ok').attr("href", criteria_id);
                        });


                    }
                });


            });
       $('#generate_report').trigger('click');
       function datatable_reinitialize() {
           return $('#all_info_table').DataTable({
               // "scrollX": true,
                "ordering": true,
               deferRender: true,
               paging:false,
               scrollY:"300px",
               "scrollCollapse": true,
                   fixedColumns:   {
                   leftColumns: 1,
                       rightColumns: 1
                   }

           });
        }
        var images = document.getElementById("images");
        const gallery = new Viewer(images,{toolbar:false,navbar:false});
        function load_img(file_path)
        {
        $('#set_image').attr('src',file_path)
        gallery.view(0);

        }

        function load_district(object) {


            div = parseInt(object.value)

            if (isNaN(parseFloat(div))) {
                $('#district').html("<option value=\"%\">Select One</option>");
                $('#upazila').html("<option value=\"%\">Select One</option>");
            }
            else {

                $.ajax({
                    url: '/asf/get_districts/',
                    type: 'POST',
                    dataType: 'json',
                    data: {'div': div},

                    success: function (result) {
                        console.log(result);
                        var html_code = "<option value=\"%\">Select One</option>";

                        for (i = 0; i < result.length; i++) {
                            html_code += "<option value=\"" + result[i].geocode + "\"> " + result[i].field_name + "</option>";
                        }
                        $('#district').html(html_code);


                    }
                });
            }

        }

        function load_upazila(dist_object) {

            dist = parseInt(dist_object.value)
            // console.log(dist);
            if (isNaN(parseFloat(dist))) {
                $('#upazila').html("<option value=\"%\">Select One</option>");

            }
            else {

                $.ajax({
                    url: '/asf/get_upazilas/',
                    type: 'POST',
                    dataType: 'json',
                    data: {'dist': dist},

                    success: function (result) {
                        console.log(result);
                        var html_code = "<option value=\"%\">Select One</option>";

                        for (i = 0; i < result.length; i++) {
                            html_code += "<option value=\"" + result[i].geocode + "\"> " + result[i].field_name + "</option>";
                        }
                        $('#upazila').html(html_code);


                    }
                });
            }

        }