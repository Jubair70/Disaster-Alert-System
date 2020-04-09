    $('#published_year').datepicker({
                format: "yyyy",
    viewMode: "years",
    minViewMode: "years"
            }).on('changeDate', function () {
                $(this).datepicker('hide');
            });