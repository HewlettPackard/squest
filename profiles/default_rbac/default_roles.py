default_roles = {
    "Organization member": {
        "description": "Can view organization",
        "permissions": [
            "profiles.view_organization"
        ]
    },
    "Team member": {
        "description": "Can view team",
        "permissions": [
            "profiles.view_team",
        ]
    },
    "Organization manager": {
        "description": "Can view and manage Organization's users.",
        "permissions": [
            "profiles.view_organization",
            "profiles.view_users_organization",
            "profiles.add_users_organization",
            "profiles.delete_users_organization",

            "profiles.add_team",
            "profiles.view_team",
            "profiles.change_team",
            "profiles.delete_team",
            "profiles.view_users_team",
            "profiles.add_users_team",
            "profiles.delete_users_team",
        ]
    },
    "Team manager": {
        "description": "Can view and manage Team's users.",
        "permissions": [
            "profiles.view_team",
            "profiles.view_users_team",
            "profiles.add_users_team",
            "profiles.delete_users_team",
        ]
    },
    "Instance viewer": {
        "description": "Can view Instance and all related objects.",
        "permissions": [
            "service_catalog.view_instance",
            "service_catalog.view_request",
            "service_catalog.view_requestmessage",
            "service_catalog.view_supportmessage",
            "service_catalog.view_support",

        ]
    },
    "Catalog user": {
        "description": "Can request services in catalog",
        "permissions": [
            "profiles.consume_quota_scope"
        ]
    },
    "Instance Operator": {
        "description": "Can request services and day 2 operations",
        "permissions": [
            "profiles.consume_quota_scope"

            "service_catalog.view_instance",
            "service_catalog.view_request",
            "service_catalog.view_requestmessage",
            "service_catalog.view_supportmessage",
            "service_catalog.view_support",

            "service_catalog.request_on_instance",
            "service_catalog.request_on_service",
            "service_catalog.cancel_request",

            "service_catalog.add_message",
            "service_catalog.view_message",
            "service_catalog.change_message",
            "service_catalog.delete_message",

            "service_catalog.add_message",
            "service_catalog.view_message",
            "service_catalog.change_message",
            "service_catalog.delete_message",

            "service_catalog.add_support",
            "service_catalog.view_support",
            "service_catalog.change_support",

        ]
    },
    "Workflow approver": {
        "description": "Can approve a step (for Approval Workflow only)",
        "permissions": [
            "service_catalog.approve_request_approvalstep"
        ]
    },
    "Request approver": {
        "description": "Can approve a request",
        "permissions": [
            "service_catalog.accept_request"
        ]
    },

}
