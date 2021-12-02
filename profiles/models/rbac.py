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
        }
}
