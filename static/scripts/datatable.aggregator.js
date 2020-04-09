 /**
 *  @name sum()
 *  @summary Sum the values in a data set.
 *
 *  @returns {Number} Summed value
 */

jQuery.fn.dataTable.Api.register( 'sum()', function ( ) {
	return this.flatten().reduce( function ( a, b ) {
		if ( typeof a === 'string' ) {
			a = a.replace(/[^\d.-]/g, '') * 1;
		}
		if ( typeof b === 'string' ) {
			b = b.replace(/[^\d.-]/g, '') * 1;
		}

		return a + b;
	}, 0 );
} );

/**
 *  @name average()
 *  @summary Average the values in a data set.
 *
 *  @returns {Number} Calculated average
 */

 jQuery.fn.dataTable.Api.register( 'average()', function () {
    var data = this.flatten();
    var sum = data.reduce( function ( a, b ) {
        return (a*1) + (b*1); // cast values in-case they are strings
    }, 0 );
 
    return parseFloat(Math.round((sum / data.length) * 100) / 100).toFixed(2);
} );


/**
 *  @name maxDate()
 *  @summary max Date the values in a data set.
 *
 *  @returns {String} Maximum date in a column


 jQuery.fn.dataTable.Api.register( 'maxDate()', function () {
    var data = this.flatten();
    var maxDate = data.reduce( function ( a, b ){
    	var aDate = moment(a,"YYYY/MM/DD");
    	var bDate = moment(b,"YYYY/MM/DD");
    	if(aDate > bDate){
    		return aDate;
    	} else {
    		return bDate;
    	} 
    }, 0)
    
    return maxDate.format("YYYY/MM/DD");
 } );

 */
 /**
 *  @name minDate()
 *  @summary min Date the values in a data set.
 *
 *  @returns {String} Minimum date in a column


 jQuery.fn.dataTable.Api.register( 'minDate()', function () {
    var data = this.flatten();
    var maxDate = data.reduce( function ( a, b ){
    	var aDate = moment(a,"YYYY/MM/DD");
    	var bDate = moment(b,"YYYY/MM/DD");
    	if(aDate < bDate){
    		return aDate;
    	} else {
    		return bDate;
    	} 
    }, 0)
    
    return maxDate.format("YYYY/MM/DD");
 } );
 */
 /**
 *  @name maxTime()
 *  @summary max Time the values in a data set.
 *
 *  @returns {String} Maximum time in a column
 */

 jQuery.fn.dataTable.Api.register( 'maxTime()', function () {
    var data = this.flatten();
    var maxTime = 0;
    if(data.length >= 1){
    	for (var i = 0; i < data.length; i++) {
    		var split_entry = data[i].split(":");
    		var actuall_entry = parseInt(split_entry[0]) * 3600 + parseInt(split_entry[1]) * 60 + parseInt(split_entry[2]);
    		if(actuall_entry > maxTime){
    			maxTime = actuall_entry;
    		}
		}
	}

    return maxTime.toHHHMMSS();
 } );


 /**
 *  @name minTime()
 *  @summary min Time the values in a data set.
 *
 *  @returns {String} Minimum time in a column
 */

 jQuery.fn.dataTable.Api.register( 'minTime()', function () {
 	var data = this.flatten();
 	var minTime = 0;
 	if(data.length >= 1){
 		for (var i = 0; i < data.length; i++) {
 			var split_entry = data[i].split(":");
 			var actuall_entry = parseInt(split_entry[0]) * 3600 + parseInt(split_entry[1]) * 60 + parseInt(split_entry[2]);
 			if(i == 0){
 				minTime = actuall_entry
 			} else {
 				if(actuall_entry < minTime){
 					minTime = actuall_entry;
 				}
 			}
 		}
 	}

    return minTime.toHHHMMSS();
 } );

/**
 *  @name averageTime()
 *  @summary average Time the values in a data set.
 *
 *  @returns {String} Average time in a column
 */
jQuery.fn.dataTable.Api.register( 'averageTime()', function (api,mulCol) {
	var data = this.flatten();
	var timeSum = 0;
	var multiplyerData = api.column( mulCol ).data();
	var multiplyerSum = 0;
	for (var k = 0; k < multiplyerData.length; k++) {
		multiplyerSum += parseInt(multiplyerData[k]);
	}
	for (var i = 0; i < data.length; i++) {
		var split_entry = data[i].split(":");
		var actuall_entry = parseInt(split_entry[0]) * 3600 + parseInt(split_entry[1]) * 60 + parseInt(split_entry[2]);
		timeSum += actuall_entry * parseInt(multiplyerData[i]);
	}
	var averageTime = Math.floor( timeSum / multiplyerSum );
	return averageTime.toHHHMMSS();
} );



 Number.prototype.toHHHMMSS = function () {
 	var sec_num = this;
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10 && hours > 0) {hours    = "0"+hours;}
    if (minutes < 10) {minutes  = "0"+minutes;}
    if (seconds < 10) {seconds  = "0"+seconds;}
    
    return hours+':'+minutes+':'+seconds;
}
