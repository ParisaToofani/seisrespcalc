$(document).ready(function() {
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
              console.log('hi')
            }
        });

    });
})
