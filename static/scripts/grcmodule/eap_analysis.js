function init_union(statesData, union_dataobj, first_color_hex, last_color_hex, highest_value, lowest_value, location_prop, location_name, range_num, map_div_id, map_height, info_div,current_date,peak_date,rank_dataobj,impact_dataobj){

    $("#"+map_div_id).css({ 'height': map_height + "px"});

    var range = [];
    var color=[];
    function getColor(union_code) {
        var d = parseFloat(union_dataobj[union_code]);
        var avg = (highest_value - lowest_value) / range_num;
        //console.log("avg === ", avg);

        range = [];
        var a = 0;
        s = range_num
        if(map_div_id=='impact_map'){
        range[a++] = 0;
        s += 1
        }

        for (i = a; i < s; i++) {
            if (i === a) {
                range[i] = lowest_value;
                continue;
            }

            range[i] = range[i - 1] + avg;
        }
        range[i] = highest_value;

        color = [];
        k = 1
        color [0] = "#d3d3d3";
        if(map_div_id == 'impact_map'){
            color[1] = "#ffff00"
            k += 1 ;
        }

        // fixed color
        given_color = []
        if(map_div_id=='mapid' || map_div_id == 'flood_peak_map')
        {
            given_color = [
            '#D8EBF2',
            '#B6DBF2',
            '#77B3D9',
            '#348ABF',
            '#0477BF'
            ]
        }
        else
        {
            given_color = [
            '#F08E93',
            '#F05050',
            '#B02024',
            '#7E1416',
            '#391212'
            ]
        }

         for(i = k, j = 0; i<=s ; i++ , j++)
            color[i] = given_color[j]
         
        // fixed color


        var flag = 0;
        for (i = 0; i < s + 1; i++) {

            if (i === 0 && d <= range[i] && range[i] == 0 ) {
                flag = 0;
                return color[0];
            } else if (d >= range[i - 1] && d <= range[i]) {
                flag = 0;
                return color[i];
            } else {
                flag = 1;
            }
        }

        if (flag === 1) {
//        console.log("okay")
            return color[0];
        }

    }

    var union_geojson = L.geoJson(statesData, {
        style: style,
        onEachFeature: onEachFeature
    });

    var bankline_layer = L.geoJson(flood_jamuna_bankline_geojson, {
        style: bankline_style,
        interactive: true
    });

//    var district_layer = L.geoJson(cyclone_district_geojson, {
//        style: district_style,
//        interactive: false
//    });
    var river_layer = L.geoJson(flood_river_geojson, {
        style: river_style,
        interactive: false
    });

    var category_layer = L.geoJson(flood_category_geojson, {
        style: category_style,
        interactive: false
    });

    // Land Mark
    // landmark color start
    landmark_color = '#F21905';
    // landmark color end

    var icon =  L.divIcon({
    html: '<i class="fas fa-circle" style="color: '+landmark_color+'; zoom:50%"></i>',
    className: 'divIcon'
    });
    var landmarks = [];
    var landmarks_layer = L.layerGroup();
    function add_landmarks()
    {
        for(i = 0; i < flood_landmarks_geojson['features'].length; i++)
        {
        L.marker([flood_landmarks_geojson['features'][i]['geometry']['coordinates'][1],flood_landmarks_geojson['features'][i]['geometry']['coordinates'][0]],{ icon:icon
        }).bindTooltip(flood_landmarks_geojson['features'][i]['properties']['DISTRICT']).addTo(landmarks_layer)

        }

    }

    add_landmarks();

    // Land Mark

    var map = L.map(map_div_id, {
        center: [25.092538, 89.2],
        zoom: 7.5,
        zoomControl: false,
        scrollWheelZoom: false,
        layers: [union_geojson, bankline_layer,river_layer,category_layer,landmarks_layer]
    });

    L.control.zoom({position: 'bottomright'}).addTo(map);

    var baseLayers = {
		"Union": union_geojson,
	};
	var overLayers = {
//	    "District": district_layer,
		"Jamuna Bankline": bankline_layer,
		"River": river_layer,
		"Land Category": category_layer,
		"Dist HQ": landmarks_layer
	};

    var switching_cntrl = L.control;
    var switching_cntrl_position = { position: 'topleft' }
	switching_cntrl.layers(baseLayers,overLayers,switching_cntrl_position).addTo(map);

    function style(feature) {
        return {
            fillColor: getColor(feature.properties[location_prop]),
            weight: 1,
            opacity: 0.8,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
        };
    }

    function bankline_style(feature) {
        return {
            weight: 2,
            opacity: 1,
            color: '#28C068',
            dashArray: '1',
            fillOpacity: 0
        };
    }

    function district_style(feature) {
            return {
                weight: 2,
                opacity: 1,
                color: '#1D1D1D',  //  #6CC6E5
                dashArray: '1',
                fillOpacity: 0
            };
    }

    function river_style(feature) {
            return {
            fillColor: '#048ABF',
                weight: 2,
                opacity: 1,
                color: '#048ABF',
                dashArray: '1',
                fillOpacity: 0.7
            };
        }

        function category_style(feature) {
            return {
                weight: 2,
                opacity: 1,
                color: '#F21D1D',
                dashArray: '1',
                fillOpacity: 0
            };
        }


    function highlightFeature(e) {
        var layer = e.target;

        layer.setStyle({
            weight: 2,
            color: '#333',
            dashArray: '',
            fillOpacity: 0.5
        });

        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
            layer.bringToFront();
        }

        info.update(layer.feature.properties);
    }

    function resetHighlight(e) {
        union_geojson.resetStyle(e.target);
        info.update();
    }

    function zoomToFeature(e) {
        map.fitBounds(e.target.getBounds());
    }

    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: zoomToFeature
        });
    }

    var info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create(info_div, 'info'); // create a div with a class "info" for hover
        this.update();
        return this._div;
    };

    info.update = function (props) {

//        if(info_div == "info_div") stru = '<h5>Flood Depth Map on ' + current_date + '</h5>'
//        if(info_div == "flood_peak_map_info_div") stru = '<h5>Flood Depth Map on ' + peak_date + ' (Peak Flood day)</h5>'
stru = ''
        if(info_div == "info_impact_map_div") stru = '<h5>Impact Based on Exposure  (' + peak_date + ')</h5>'
        else if(info_div == "info_potential_map_div") stru = '<h5>Potential Intervention Area  ( ' + peak_date + ')</h5>'
        this._div.innerHTML =  stru + (props ?
//            '<b>' + props[location_name] + '</b><br />' +union_dataobj[props[location_prop]] + ''
'<b>' + props[location_name] + '</b> ' +(typeof union_dataobj[props[location_prop]]==='undefined'?'':' ('+union_dataobj[props[location_prop]] +') ') + (map_div_id=='potential_map'?'<br>Rank: '+(typeof rank_dataobj[props[location_prop]]==='undefined'?'':rank_dataobj[props[location_prop]])  +(typeof impact_dataobj[props[location_prop]]==='undefined'?'':' ('+impact_dataobj[props[location_prop]]+')'):'')
            : 'Hover over a state');
    };

    info.addTo(map);

    var legend = L.control({position: 'bottomleft'});
    legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend'),
            labels = [],
            from, to;
//            <span style="background: #1D1D1D;"></span>District<br>
            lbl_geographic_line = '<div class="mb-2 mr-2 badge badge-alternate">Data Source: '+file_source+'</div><br><div class="mb-2 mr-2 badge badge-secondary">boundary</div><br><i class="fas fa-circle" style="color: '+landmark_color+'; zoom: 50%; margin-right: 102.5px; margin-top: 14px;"></i>Dist HQ<br><span style="background-color: white;"></span>Union<br><span style="background: #28C068;"></span>Bankline<br><span style="background: #048ABF;"></span>River<br><span style="background: #F21D1D;"></span>Land Category<br>'
            labels.push(lbl_geographic_line);
            if(map_div_id=='mapid'){
            $('#info_div_blk').text('Flood Depth Map on ' + current_date );
            labels.push('<div class="mb-2 mr-2 badge badge-secondary">flood depth (m)</div>');
            }

            else if (map_div_id=='flood_peak_map')
            {
            $('#peak_div_blk').text('Flood Depth Map on ' + peak_date + ' (Peak Flood day)')
            labels.push('<div class="mb-2 mr-2 badge badge-secondary">flood depth (peak)(m)</div>');
            }

            else if (map_div_id=='impact_map')
            labels.push('<div class="mb-2 mr-2 badge badge-secondary">impact</div>');
            else if (map_div_id=='potential_map')
            labels.push('<div class="mb-2 mr-2 badge badge-secondary">potential intervention</div>');
        for (var i = 0; i < range.length+2; i++) {
            from = parseFloat(range[i]).toFixed(2);
            to = range[i + 1];
            if(!to) break; 
            else 
                {

                    to = parseFloat(range[i+1]).toFixed(2);
                    to = (to - 0.01).toFixed(2);
                }

            if(from==0.0)
                from = (parseFloat(from) + 0.01).toFixed(2);

            labels.push('<i style="width: 18px;height: 18px;float: left;margin-right: 8px;opacity: 0.7;background:' + color[i+1] + '"></i> ' + from + (to ? ' &ndash; ' + to : '+') + '<br>');
        }
        div.innerHTML = labels.join('<br>');
        return div;
    };
    legend.addTo(map);


}
$('#flood_depth_level_div').hide();
$('#impact_div').hide();
$('#potential_div').hide();

// console.log("geojson_data =========== ", geojson_data);
flood_depth_level_div_cntrl = 0
impact_div_cntrl = 0
potential_div_cntrl  = 0


     $( "#flood-data-btn" ).click(function() {
          $('#flood_depth_level_div').show();
          $('#impact_div').hide();
          $('#potential_div').hide();
          $('#flood-data-btn').addClass("selected_btn");
          $('#impact_btn').removeClass("selected_btn");
          $('#potential_btn').removeClass("selected_btn");
          if(!flood_depth_level_div_cntrl){
            flood_depth_level_div_cntrl = 1
            flood_data();
          }

     });

      $('#impact_btn').click(function() {
         $('#flood_depth_level_div').hide();
        $('#impact_div').show();
        $('#potential_div').hide();
        $('#flood-data-btn').removeClass("selected_btn");
        $('#impact_btn').addClass("selected_btn");
        $('#potential_btn').removeClass("selected_btn");
        if(!impact_div_cntrl){
            impact_div_cntrl = 1
            impact_data();
          }

     });

     $('#potential_btn').click(function() {
            $('#flood_depth_level_div').hide();
            $('#impact_div').hide();
            $('#potential_div').show();
            $('#flood-data-btn').removeClass("selected_btn");
            $('#impact_btn').removeClass("selected_btn");
            $('#potential_btn').addClass("selected_btn");
            if(!potential_div_cntrl)
            {
            potential_div_cntrl = 1
            potential_data();
            }

     });

     function flood_data(){
     $.ajax({
                    url: '/modules/flood_depth_data/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                    },
                    beforeSend: function () {
                    },
                    success: function (data_list) {
                    var all_data = data_list['df']
                    var vul_index_arr = data_list['var_list']
                    var union_dataobj = data_list['df_obj'];
                    var current_date = data_list['curr_date'];
                    var peak_date = data_list['peak_date'];
                    var vul_index_arr_peak = data_list['flood_peak_list'];
                    var curr_date = data_list['curr_date']
                    var peak_date = data_list['peak_date']
                    var columns = [];
                    var col_val = ["div_name", "dist_name", "upz_name", "union_name", "union_code", "category_label", "current_flood_depth", "peak_flood_depth"]
                    col_val.forEach(myFunction);

                      function myFunction(item) {
                        var col_obj = {};
                        col_obj["data"] = item;
                        columns.push(col_obj);
                      }
                  $('#curr_date').text(curr_date);
                  $('#peak_date').text(peak_date);
                  var table_id = "data-flood-depth";
//                  console.log(all_data, table_id, columns)
                  showdatatable(all_data, table_id, columns);

                 var highest_value = Math.max(...vul_index_arr);
                 var lowest_value = Math.min(...vul_index_arr);
                    var first_color_hex = "#d80000";
                 var last_color_hex = "#3f0000";
                 var location_prop = "Union_Code";
                 var location_name = "UNI_NAME";
                 var range_num = 5;
                 var map_div_id = "mapid";
                 var map_height = 600;
                 var info_div = "info_div";
                init_union(geojson_data, union_dataobj, first_color_hex, last_color_hex, highest_value, lowest_value, location_prop, location_name, range_num, map_div_id, map_height, info_div,current_date,peak_date,{},{});
                 var highest_value_peak = Math.max(...vul_index_arr_peak);
                 var lowest_value_peak = Math.min(...vul_index_arr_peak);
                 var map_div_id_peak = "flood_peak_map";
                 var info_div_peak = "flood_peak_map_info_div";
         init_union(geojson_data, union_dataobj, first_color_hex, last_color_hex, highest_value_peak, lowest_value_peak, location_prop, location_name, range_num, map_div_id_peak, map_height, info_div_peak,current_date,peak_date,{},{});

                    }
                });
     }


     function impact_data (){
     $.ajax({
                    url: '/modules/flood_impact_data/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                    },
                    beforeSend: function () {
                    },
                    success: function (data_list) {

                    var all_data = data_list['df']
                    var vul_index_impact = data_list['impact_list']
                    var impact_dataobj = data_list['df_impact'];
                     var current_date = data_list['curr_date'];
                    var peak_date = data_list['peak_date'];
                    var columns = [];
                    var col_val = ["div_name", "dist_name", "upz_name", "union_name","union_code", "category_label",  "peak_flood_depth", "impact"]
                    col_val.forEach(myFunction);

                      function myFunction(item) {
                        var col_obj = {};
                        col_obj["data"] = item;
                        columns.push(col_obj);
                      }
                  $('#impt_peak_date').text(peak_date);
                  var table_id = "impact_tbl";
//                  console.log(all_data, table_id, columns)
                  showdatatable(all_data, table_id, columns);

                 var highest_value = Math.max(...vul_index_impact);
//         var lowest_value = Math.min(...vul_index_impact);
var lowest_value = 0.25
      var first_color_hex = "#d80000";
                 var last_color_hex = "#3f0000";
         var location_prop = "Union_Code";
         var location_name = "UNI_NAME";
         var range_num = 5;
         var map_div_id = "impact_map";
         var map_height = 600;
         var info_div = "info_impact_map_div";

         init_union(geojson_data, impact_dataobj, first_color_hex, last_color_hex, highest_value, lowest_value, location_prop, location_name, range_num, map_div_id, map_height, info_div,current_date,peak_date,{},{});

                    }
                });
     }


     function potential_data(){
     $.ajax({
                    url: '/modules/flood_potential_data/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                    },
                    beforeSend: function () {
                    },
                    success: function (data_list) {
                    var all_data = data_list['df']
                    var vul_index_potential = data_list['potential_list']
                    var potential_dataobj = data_list['df_potential'];
                    var rank_dataobj = data_list['df_rank'];
                    var impact_dataobj = data_list['df_impact'];
                     var current_date = data_list['curr_date'];
                    var peak_date = data_list['peak_date'];
                    var columns = [];
                    var col_val = ["div_name", "dist_name", "upz_name", "union_name","union_code", "category_label",  "peak_flood_depth", "impact","vulnaribity_index","potential_damage","potential_damage_rank"]
                    col_val.forEach(myFunction);

                      function myFunction(item) {
                        var col_obj = {};
                        col_obj["data"] = item;
                        columns.push(col_obj);
                      }
                  $('#pot_peak_date').text(peak_date);
                  var table_id = "potential_tbl";
//                  console.log(all_data, table_id, columns)
                  showdatatable(all_data, table_id, columns);

               var highest_value = Math.max(...vul_index_potential);
            var lowest_value = Math.min(...vul_index_potential);
           var first_color_hex = "#d80000";
                 var last_color_hex = "#3f0000";
         var location_prop = "Union_Code";
         var location_name = "UNI_NAME";
         var range_num = 5;
         var map_div_id = "potential_map";
         var map_height = 600;
         var info_div = "info_potential_map_div";

                init_union(geojson_data, potential_dataobj, first_color_hex, last_color_hex, highest_value, lowest_value, location_prop, location_name, range_num, map_div_id, map_height, info_div,current_date,peak_date,rank_dataobj,impact_dataobj);

                    }
                });
     }


// need to fix it
$.fn.dataTable.ext.errMode = 'none';
function showdatatable(all_data, table_id, columns){
     if(table_id=='potential_tbl')
         $('#'+table_id).DataTable({
               "data": all_data,
               "columns": columns,
               "scrollX": true,
               dom: 'Bfrtip',
               buttons: [
                    {
                        filename: "Exported Data",
                        title: "",
                        text: "<strong>Export</strong>",
                        extend: 'excelHtml5'
                    }
                ]
         });
         else $('#'+table_id).DataTable({
               "data": all_data,
               "columns": columns,
               dom: 'Bfrtip',
               buttons: [
                    {
                        filename: "Exported Data",
                        title: "",
                        text: "<strong>Export</strong>",
                        extend: 'excelHtml5'
                    }
                ]
         });

     }
$('#flood-data-btn').trigger('click');

