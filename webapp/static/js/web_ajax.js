$(document).ready(function() {
    $('input[type="file"]').change(function(e){
        var fileName = e.target.files[0].name;
        alert('The file "' + fileName +  '" has been selected.');
    });
    $('#calculate').click(function(e){
        e.preventDefault();
        var file = $('#motion').files[0];
        var number_of_stories = $('#number_of_stories').val();
        var stories_height = $('#stories_height').val();
        var building_type_hazus = $('#building_type_hazus').val();
        var stories_mass = $('#stories_mass').val();
        var seismic_design_category = $('#seismic_design_category').val();
        var d_t = $('#d_t').val();
        var stories_area = []
        for (var floor=1; floor<=(number_of_stories); floor++){
            var story_area = $("[name='story_area-"+ floor +"']").val();
            stories_area.push(story_area);
        }
        // ---------------------------------------
        // validate_input
        // ---------------------------------------
        if(validate_input("lat")) return;
        if(validate_input("lng")) return;
        if(validate_input("number_of_stories")) return
        for (var j=1; j<=(number_of_stories); j++) {
            if ($("[name=story_area-"+ (j) +"]").val()==""){
                $("[name=story_area-"+ (j) +"]").parent().addClass("has-error")
                alert("مساحت طبقات تکمیل شود.")
                document.getElementsByName('story_area-'+ (j) +'')[0].scrollIntoView({behavior: "smooth", inline: "nearest"})
                return}
        }
        // --------------------------------------------------------
        // get url
        // --------------------------------------------------------
        // Request the '/study/site_hazard/' url and send some additional data to the view.py def 
        // $.get( 'url', {data}):
        $.get('/study/total_demolition_estimation/', {lat: lat, lng: lng, stories_area: stories_area}, function(data){
                                                      $('#total_demolition').val(data)
                                                    //   window.price = data
        });

    });
})