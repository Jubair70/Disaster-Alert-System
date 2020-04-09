function init_union(statesData, union_dataobj, first_color_hex, last_color_hex, highest_value, lowest_value, location_prop, location_name, range_num, map_div_id, map_height, info_div){
    // console.log("This is union js !");

    $("#"+map_div_id).css({ 'height': map_height + "px" });

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
        given_color = [
            '#D8EBF2',
            '#B6DBF2',
            '#77B3D9',
            '#348ABF',
            '#0477BF'
            ]

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

    var sundarban_layer = L.geoJson(sundarban_geojson, {
        style: sundarban_style,
    interactive: true
    });

    var district_layer = L.geoJson(cyclone_district_geojson, {
        style: district_style,
    interactive: false
    });
    var river_layer = L.geoJson(cyclone_river_geojson, {
        style: river_style,
        interactive: false
    });

    var zone_layer = L.geoJson(cyclone_zone_geojson, {
        style: zone_style,
        interactive: false
    });

    // Land Mark
    // landmark color start
    landmark_color = '#335928';
    // landmark color end

    var icon =  L.divIcon({
    html: '<i class="fas fa-1x fa-circle" style="color: '+landmark_color+'"></i>',
    className: 'divIcon'
    });
    var landmarks = [];
    var landmarks_layer = L.layerGroup();
    function add_landmarks()
    {
        for(i = 0; i < cyclone_landmarks['features'].length; i++)
        {
        L.marker([cyclone_landmarks['features'][i]['geometry']['coordinates'][1],cyclone_landmarks['features'][i]['geometry']['coordinates'][0]],{ icon:icon
        }).bindTooltip(cyclone_landmarks['features'][i]['properties']['DISTRICT']).addTo(landmarks_layer)

        }

    }

    add_landmarks();

    // Land Mark

    var map = L.map(map_div_id, {
        center: [22.150075806124867, 90.37353515625],
        zoom: 7.5,
        zoomControl: false,
        scrollWheelZoom: false,
        layers: [union_geojson,sundarban_layer,district_layer,river_layer,zone_layer,landmarks_layer]
    });

   L.control.zoom({position: 'bottomright'}).addTo(map);

    var baseLayers = {
		"Union": union_geojson,
	};
	var overLayers = {
	    "District": district_layer,
		"Sundarban": sundarban_layer,
		"River": river_layer,
		"Coastal Zone": zone_layer,
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

    function sundarban_style(feature) {
        return {
            fillColor: '#28C068',
            weight: 1,
            opacity: 0.8,
            color: '#28C068',
            dashArray: '1',
            fillOpacity: 0.7
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

        function zone_style(feature) {
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
        this._div = L.DomUtil.create(info_div, 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    info.update = function (props) {
    stru = '<h5>Vulnerability Index</h5>'

        this._div.innerHTML =  stru +  (props ?
            '<b>' + props[location_name] + '</b><br/>' +union_dataobj[props[location_prop]] + ''
            : 'Hover over a state');
    };

    info.addTo(map);
    var legend = L.control({position: 'bottomleft'});
    legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend'),
            labels = [],
            from, to;
            lbl_geographic_line = '<div class="mb-2 mr-2 badge badge-secondary">boundary</div><br><i class="fas fa-circle" style="color: '+landmark_color+'; margin-right:42.5px"></i>Dist HQ<br><span style="background-color: white;"></span>Union<br><span style="background: #1D1D1D;"></span>District<br><span style="background: #28C068;"></span>Sundarban<br><span style="background: #048ABF;"></span>River<br><span style="background: #F21D1D;"></span>Coastal Zone<br>'
            labels.push(lbl_geographic_line);
        labels.push('<div class="mb-2 mr-2 badge badge-secondary">Vulnerability Index</div>');
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

flood_index_data();
     function flood_index_data(){

                  var columns = [];
                  var col_val = ["div_name", "dist_name", "upz_name", "union_name", "zone_label", "vulnaribity_index"]
                  col_val.forEach(myFunction);

                  function myFunction(item) {
                    var col_obj = {};
                    col_obj["data"] = item;
                    columns.push(col_obj);
                  }
                 $('#latest_date').text(latest_date);
                 var table_id = "data-flood-depth";
                 showdatatable(all_data, table_id, columns);

                 var highest_value = Math.max(...vul_index_arr);
                 var lowest_value = Math.min(...vul_index_arr);
                 var first_color_hex = '#D80000';
                 var last_color_hex = '#3F0000';
                var location_prop = "UNICODE11";
                 var location_name = "UNIONNAME";
                 var range_num = 5;
                 var map_div_id = "mapid";
                 var map_height = 600;
                 var info_div = "info_div";
                 init_union(geojson_data, union_dataobj, first_color_hex, last_color_hex, highest_value, lowest_value, location_prop, location_name, range_num, map_div_id, map_height, info_div);

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