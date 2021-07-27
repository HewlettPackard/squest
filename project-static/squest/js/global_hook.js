function load_state(model, default_option_value){
    var url = $("#GlobalHookForm").attr("data-state-url");  // get the url of the `load_states` view
    $.ajax({
        url: url,
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'model': model
        },
        success: function (data) {
            $("#id_state").html(data);
            if (typeof default_option_value != 'undefined') {
                document.getElementById('id_state').value=default_option_value;
            }
        }
    });
}
