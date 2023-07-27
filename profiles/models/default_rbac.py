roles_list = {
    "Organization administrator": {
        "description": "An administrator of the organization can view and manage the Organization and all Objects linked.",
        "model_names": {
            "profiles.organization": {
                "permissions": [
                    "view_organization",
                    "view_users_organization",
                    "add_users_organization",
                    "delete_users_organization",
                ]
            },
            "profiles.team": {
                "permissions": [
                    "add_team",
                    "view_team",
                    "change_team",
                    "delete_team",
                    "view_users_team",
                    "add_users_team",
                    "delete_users_team",
                ]
            },
            "service_catalog.instance": {
                "permissions": [
                    "view_instance",
                    "request_on_instance",
                ]
            },
            "service_catalog.request": {
                "permissions": [
                    "cancel_request",
                    "view_request",
                ]
            },
            "service_catalog.requestmessage": {
                "permissions": [
                    "add_requestmessage",
                    "view_requestmessage",
                    "change_requestmessage",
                    "delete_requestmessage",
                ]
            },
            "service_catalog.supportmessage": {
                "permissions": [
                    "add_supportmessage",
                    "view_supportmessage",
                    "change_supportmessage",
                    "delete_supportmessage",
                ]
            },
            "service_catalog.support": {
                "permissions": [
                    "add_support",
                    "view_support",
                    "change_support",
                    "delete_support",
                ]
            },
        }
    },
    "Team administrator": {
        "description": "An administrator of the organization can view and manage the Team and all Objects linked.",
        "model_names": {
            "profiles.team": {
                "permissions": [
                    "view_team",
                    "view_users_team",
                    "add_users_team",
                    "delete_users_team",
                ]
            },
            "service_catalog.instance": {
                "permissions": [
                    "view_instance",
                    "request_on_instance",
                ]
            },
            "service_catalog.request": {
                "permissions": [
                    "cancel_request",
                    "view_request",
                ]
            },
            "service_catalog.requestmessage": {
                "permissions": [
                    "add_requestmessage",
                    "view_requestmessage",
                    "change_requestmessage",
                    "delete_requestmessage",
                ]
            },
            "service_catalog.supportmessage": {
                "permissions": [
                    "add_supportmessage",
                    "view_supportmessage",
                    "change_supportmessage",
                    "delete_supportmessage",
                ]
            },
            "service_catalog.support": {
                "permissions": [
                    "add_support",
                    "view_support",
                    "change_support",
                    "delete_support",
                ]
            },
        },
    },
    # "Approver": {
    #     "description": "An approver can approve approval step linked to his Group (Organization or Team)",
    #     "model_names": {
    #         "service_catalog.approvalstep": {
    #             "permissions": [
    #                 "approve_request_approvalstep"
    #             ]
    #         }
    #     }
    # },
    "Organization member": {
        "description": "A member can access the members of the organization",
        "model_names": {
            "profiles.organization": {
                "permissions": [
                    "view_organization"
                ]
            }
        }
    },
    "Team member": {
        "description": "An member of the team",
        "model_names": {
            'profiles.scope': {
                'permissions': [
                    'consume_quota_scope'
                ]
            },
            "profiles.team": {
                "permissions": [
                    "view_team",
                    "view_users_team",
                ]
            },
            "service_catalog.instance": {
                "permissions": [
                    "view_instance",
                    "request_on_instance",
                ]
            },
            "service_catalog.request": {
                "permissions": [
                    "cancel_request",
                    "view_request",
                ]
            },
            "service_catalog.operation": {
                "permissions": [
                    "list_operation",
                ]
            },
            "service_catalog.supportmessage": {
                "permissions": [
                    "add_message",
                    "view_message",
                    "change_message",
                    "delete_message",
                ]
            },
            "service_catalog.requestmessage": {
                "permissions": [
                    "add_message",
                    "view_message",
                    "change_message",
                    "delete_message",
                ]
            },
            "service_catalog.support": {
                "permissions": [
                    "add_support",
                    "view_support",
                    "change_support",
                    "delete_support",
                ]
            },
        },
    }
}
