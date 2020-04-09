            var table = $('#all_info_table').DataTable({
//                "scrollX": true,
                "ordering": false,
//                deferRender: true,
                pagination:false,
                scrollCollapse: true,
                exporting:true
//                ,
//                fixedColumns:   {
//                    leftColumns: 1,
//                    rightColumns: 1
//                }
            });

 $(".paginate_button").hide();
             $('#generate_report').on('click', function (e) {

               table.destroy();


                var from_date   = $('#from_date').val();
                var to_date     = $('#to_date').val();


                $.ajax({
                    url: '/modules/get_dashboard_data/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        'from_date':from_date
                        ,'to_date':to_date

                    },
                    beforeSend: function () {

                    },
                    success: function (result) {
                    console.log(result)
                            list = result.tbl_data
                            page_num = result.page_num

                            var tbody = '';

                        for (var idx in list) {
                            if(parseFloat(list[idx].forecast_water_level)>=19.50 && parseFloat(list[idx].forecast_water_level)<20.35)
                                tbody +='<tr style="color:blue">'
                            else if(parseFloat(list[idx].forecast_water_level)>=20.35)
                                tbody +='<tr style="color:red">'
                            else tbody +='<tr>'

                            tbody += '<td>' + list[idx].file_source + '</td><td>' + list[idx].flood_watch +'</td><td>' +  (list[idx].forecast_water_level == '0'  ? '':list[idx].forecast_water_level)  +'</td><';
                            tbody +='</tr>'
                        }
                        $("#all_info_table").find('tbody').html(tbody);
                       table = datatable_reinitialize();
                       table.page(page_num).draw( 'page' );

                            title_txt = "Hydrograph"
                            con_name = "flood_container"
                            categories = result.flood_watch
                             data = result.forecast_water_level
                           highcharts(title_txt,con_name,categories, data);

                    }
                });


            });
       $('#generate_report').trigger('click');
       function datatable_reinitialize() {
           return $('#all_info_table').DataTable({
               // "scrollX": true,
                "ordering": true,
               deferRender: true,
               paging:true,
               pagingType: "simple",
               dom: 'Bfrtip',
                buttons: [
                    {
                        filename: "Flood Forecast Water Level",
                        title: "",
                        text: "<strong>Export</strong>",
                        extend: 'excel'
                    }
                ],
//               scrollY:"300px",
               "scrollCollapse": true,
               searching:false
//                   fixedColumns:   {
//                   leftColumns: 1,
//                       rightColumns: 1
//                   }

           });
        }


function highcharts(title_txt,con_name,categories, data) {
                Highcharts.setOptions({lang: {noData: "No Data Available"}});
              Highcharts.chart(con_name, {
                chart: {

                    type: 'line',
                     zoomType: 'x',
    events: {
      load: function () {
        var catLen = this.xAxis[0].categories.length - 1;
        this.xAxis[0].setExtremes(catLen - 5, catLen);
      },
      selection:function(){
      return false;
      }
    },
                },

                title: {
                    text: title_txt
                },
                xAxis: {

                    categories: categories,
                    min: 0,
                    max: Math.min(5, categories.length - 1)

                },
                yAxis: {
                    title: {
                        text: ''
                    },
//                    ,plotBands: [{
//    color: 'blue', // Color value
//    from: 19.50, // Start of the plot band
//    to: 20.35 // End of the plot band
//  }],
                  plotLines: [{
                    color: 'blue', // Color value
                    value:19.50, // Value of where the line will appear
                    width: 2, // Width of the line
                    label: {
        text: 19.50,
        textAlign: 'left',
        x: -40,
        y: 5,
                style: {
                    color: 'blue',
                    fontWeight: 'bold'
                }
    }
                  },{
                    color: 'red', // Color value
                    dashStyle: 'longdashdot', // Style of the plot line. Default to solid
                    value: 20.35, // Value of where the line will appear
                    width: 2, // Width of the line
                    label: {
        text: 20.35,
        textAlign: 'left',
        x: -40,
        y: 5,
                style: {
                    color: 'red',
                    fontWeight: 'bold'
                }
    }
                  }]
                },
                legend: {
                    enabled: false,
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle'
                },

                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        }
                    },
                    series: {
                        label: {
                            enabled: false
                        }
                    }

                },

                series: [{name: "water level", data: data
                ,
                dataLabels: {
                    enabled: true,
                    rotation: -90,
                    color: '#FFFFFF',
                    align: 'right',
                    format: '{point.y:.1f}', // one decimal
                    y: 10, // 10 pixels down from the top
                    style: {
                        fontSize: '13px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
                }]
                ,
                scrollbar: {
                    enabled: false,
                    barBackgroundColor: 'gray',
                    barBorderRadius: 7,
                    barBorderWidth: 0,
                    buttonBackgroundColor: 'gray',
                    buttonBorderWidth: 0,
                    buttonArrowColor: 'yellow',
                    buttonBorderRadius: 7,
                    rifleColor: 'yellow',
                    trackBackgroundColor: 'white',
                    trackBorderWidth: 1,
                    trackBorderColor: 'silver',
                    trackBorderRadius: 7
                }
                ,
                exporting: {
                    sourceWidth: 120 * categories.length,
                    sourceHeight: 500,
                    chartOptions: {
                        xAxis: [{
                            categories: categories,
                            min: 0,
                            max: categories.length - 1
                        }],
                        scrollbar: {
                            enabled: false
                        }

                    }

                }
                , credits:
                    {
                        enabled: false
                    }
                    ,
                loading: {
        hideDuration: 1000,
        showDuration: 1000
    }

            });
        }