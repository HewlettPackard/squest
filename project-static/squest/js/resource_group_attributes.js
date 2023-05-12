function load_resource_group_attributes(target_resource_group_id){
    var url = $("#ResourceGroupLinkForm").attr("data-attribute-url");
    var current_resource_group_id = $("#ResourceGroupLinkForm").attr("current-resource-group-id");
    $.ajax({
        url: url,
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'current_resource_group_id': current_resource_group_id,
            'target_resource_group_id': target_resource_group_id
        },
        success: function (data) {
            $("#id_consume_from_attribute_id").html(data);
        },
        error: function(){
            console.log("Error during ajax call 'load_resource_group_attributes'");
        }
    });
}
