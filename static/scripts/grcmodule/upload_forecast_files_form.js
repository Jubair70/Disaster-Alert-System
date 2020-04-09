    $('#forecast_date').datepicker({
                endDate: '0d',
                format: 'dd/mm/yyyy',
                todayHighlight: true
            }).on('changeDate', function () {
                $(this).datepicker('hide');
            });