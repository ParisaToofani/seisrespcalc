$(document).ready(function() {
    function chart_generator(container_id, x_axis_name, required_data){
        Highcharts.chart(container_id, {
            chart: {
                type: 'spline',
                inverted: true,
                borderColor: '#EBBA95',
                borderWidth: 2,
            },
            title:{
                text: null
            },
            
            xAxis: {
                reversed: false,
                title: {
                    enabled: true,
                    text: 'Floor'
                },
                maxPadding: 0.05,
                showLastLabel: true
            },
            yAxis: {
                title: {
                    text: x_axis_name
                },
                lineWidth: 2
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                spline: {
                    marker: {
                        enable: false
                    }
                }
            },
            series: [{
                data: required_data
            }]
        });
    }
    // ==========================================================
    function chart_generator_rec(container_id, x_axis_name, y_axis_name, required_data){
        Highcharts.chart(container_id, {
            chart: {
                type: 'line',
                inverted: true,
                borderColor: '#EBBA95',
                borderWidth: 2,
            },
            title:{
                text: null
            },
            
            xAxis: {
                reversed: false,
                title: {
                    enabled: true,
                    text: y_axis_name
                },
                maxPadding: 0.05,
                showLastLabel: true
            },
            yAxis: {
                title: {
                    text: x_axis_name
                },
                lineWidth: 2
            },
            legend: {
                enabled: false
            },
            series: [{
                data: required_data
            }]
        });
    }
    // ===================================================================
    $('input[type="file"]').change(function(e){
        var fileName = e.target.files[0].name;
        alert('The file "' + fileName +  '" has been selected.');
    });
    
    $('form #calculate').click(function(e){
        e.preventDefault()
        var form_data = new FormData(document.getElementById("main_form"));
        $.ajax({
            type: 'POST',
            url: 'resp_estimate/',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
            var disp_each_story_max = data.disp_each_story_max
            var vel_each_story_max = data.vel_each_story_max
            var accel_each_story_max = data.accel_each_story_max
            var drift_each_story_max = data.drift_each_story_max
            //   
            var period = data.periods
            var spec = data.spec
            var eq = data.eq
            var rec_d_t = data.rec_d_t
            //   Moddified Data
            var disp = []
            var vel = []
            var accel = []
            var drift = []
            // Building Results
            for(var j=0; j<(disp_each_story_max.length); j++){
                disp.push([j, disp_each_story_max[j]])
                vel.push([j, vel_each_story_max[j]])
                accel.push([j, accel_each_story_max[j]])
                drift.push([j, drift_each_story_max[j]])
            }
            // Time History
            console.log(eq)
            timehistory = []
            for(var j=0; j<(eq.length); j++){
                timehistory.push([eq[j], rec_d_t[j]])
            }
            // Spectrum
            spectrum = []
            for(var j=0; j<(period.length); j++){
                spectrum.push([spec[j], period[j]])
            }
            $('#main_results').css('display', 'block')
            $('#spec_results').css('display', 'block')
            chart_generator('container_disp', 'Displacement (m)', disp)
            chart_generator('container_accel', 'Acceleration (g)', accel)
            chart_generator('container_drift', 'Drift', drift)
            chart_generator_rec('container_rec', 'Time (s)', 'Acceleration (g)', timehistory)
            chart_generator_rec('container_spec', 'Period (s)', 'Spectral Acceleration (g)', spectrum)
            }
        });

    });
})
