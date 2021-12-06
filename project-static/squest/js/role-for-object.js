function get_users_with_role(role_id){
    var url = $("#UserRoleForObjectForm").attr("data-get-users-with-role-url");
    var content_type_id = $("#UserRoleForObjectForm").attr("data-content-type-id");
    var object_id = $("#UserRoleForObjectForm").attr("data-object-id");
    $.ajax({
        url: url,
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'role_id': role_id,
            'content_type_id': content_type_id,
            'object_id': object_id
        },
        success: function (data) {
            console.log(data);
            $("#id_users").html(data);
            $("#id_users").selectpicker('refresh');
        },
        error: function(){
            console.log("Error during ajax call 'get_users_with_role'");
        }
    });
}

function get_teams_with_role(role_id){
    var url = $("#TeamRoleForObjectForm").attr("data-get-teams-with-role-url");
    var content_type_id = $("#TeamRoleForObjectForm").attr("data-content-type-id");
    var object_id = $("#TeamRoleForObjectForm").attr("data-object-id");
    $.ajax({
        url: url,
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'role_id': role_id,
            'content_type_id': content_type_id,
            'object_id': object_id
        },
        success: function (data) {
            console.log(data);
            $("#id_teams").html(data);
            $("#id_teams").selectpicker('refresh');
        },
        error: function(){
            console.log("Error during ajax call 'get_teams_with_role'");
        }
    });
}
