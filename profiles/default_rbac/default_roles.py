default_roles = {
    "Squest user": {
        "description": "Can view organization",
        "permissions": [
            "profiles.consume_quota_scope",
            "service_catalog.request_on_instance",
            "service_catalog.request_on_service",

            "profiles.view_organization",

            "profiles.view_team",
            "profiles.add_team",
            "profiles.view_team",
            "profiles.change_team",
            "profiles.delete_team",

            "profiles.view_users_team",
            "profiles.add_users_team",
            "profiles.delete_users_team",

            "service_catalog.view_instance",
            "service_catalog.archive_instance",
            "service_catalog.unarchive_instance",
            "service_catalog.rename_instance",
            "service_catalog.change_requester_on_instance",

            "service_catalog.view_request",
            "service_catalog.cancel_request",
            "service_catalog.archive_request",
            "service_catalog.unarchive_request",

            "service_catalog.view_requestmessage",
            "service_catalog.add_requestmessage",
            "service_catalog.change_requestmessage",

            "service_catalog.view_support",
            "service_catalog.add_support",
            "service_catalog.change_support",

            "service_catalog.view_supportmessage",
            "service_catalog.add_supportmessage",
            "service_catalog.change_supportmessage",

            "profiles.view_quota",
        ]
    }
}
