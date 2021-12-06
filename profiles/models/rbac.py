roles_config = {
    "profiles.team":
        {
            "Admin": {
                "description": "An administrator of the team can manage it",
                "permissions": [
                    "change_team",
                    "delete_team",
                    "view_team"
                ]
            },
            "Member": {
                "description": "A member can access the members of the team",
                "permissions": [
                    "view_team"
                ]
            }
        },
    "service_catalog.instance":
        {
            "Admin": {
                "description": "An administrator of the instance can manage it",
                "permissions": [
                    "change_instance",
                    "view_instance"
                ]
            },
            "User": {
                "description": "A user can ask for operations on the instance",
                "permissions": [
                    "ask_instance",
                    "view_instance"
                ]
            },
            "Reader": {
                "description": "A reader can access the instance",
                "permissions": [
                    "view_instance"
                ]
            }
        }
}
