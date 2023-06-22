roles_list = {
    "Organization administrator": {
        "description": "An administrator of the organization can view and manage the Organization and all Objects linked.",
        "model_names": {
            "profiles.organization": {
                "permissions": [
                    "view_organization",
                    "view_users_organization",
                    "edit_users_organization",
                ]
            },
            # "profiles.team": {
            #     "permissions": [
            #         "create_team",
            #         "view_team",
            #         "edit_team",
            #         "delete_team",
            #         "view_users_team",
            #         "edit_users_team",
            #     ]
            # },
            "service_catalog.instance": {
                "permissions": [
                    "view_instance",
                    "request_operation_on_instance",
                    "request_support_on_instance",
                ]
            },
            "service_catalog.request": {
                "permissions": [
                    "comment_request",
                    "cancel_request",
                    "view_request",
                ]
            },
            # "service_catalog.message": {
            #     "permissions": [
            #         "create_message",
            #         "view_message",
            #         "edit_message",
            #         "delete_message",
            #     ]
            # },
            "service_catalog.support": {
                "permissions": [
                    "create_support",
                    "view_support",
                    "edit_support",
                    "delete_support",
                ]
            },
        }
    },
    "Team administrator": {
        "description": "An administrator of the organization can view and manage the Team and all Objects linked.",
        "model_names": {
            # "profiles.team": {
            #     "permissions": [
            #         "view_team",
            #         "view_users_team",
            #         "edit_users_team",
            #     ]
            # },
            "service_catalog.instance": {
                "permissions": [
                    "view_instance",
                    "request_operation_on_instance",
                    "request_support_on_instance",
                ]
            },
            "service_catalog.request": {
                "permissions": [
                    "comment_request",
                    "cancel_request",
                    "view_request",
                ]
            },
            # "service_catalog.message": {
            #     "permissions": [
            #         "create_message",
            #         "view_message",
            #         "edit_message",
            #         "delete_message",
            #     ]
            # },
            "service_catalog.support": {
                "permissions": [
                    "create_support",
                    "view_support",
                    "edit_support",
                    "delete_support",
                ]
            },
        },
    },
    "Approver": {
        "description": "An approver can approve approval step linked to his Group (Organization or Team)",
        "model_names": {
            "service_catalog.approvalstep": {
                "permissions": [
                    "approve_request_approvalstep"
                ]
            }
        }
    },
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
        "description": "An administrator of the organization can manage it",
        "model_names": {
            # "profiles.team": {
            #     "permissions": [
            #         "view_team",
            #         "view_users_team",
            #     ]
            # },
            "service_catalog.instance": {
                "permissions": [
                    "view_instance",
                    "request_operation_on_instance",
                    "request_support_on_instance",
                ]
            },
            "service_catalog.request": {
                "permissions": [
                    "comment_request",
                    "cancel_request",
                    "view_request",
                ]
            },
            # "service_catalog.message": {
            #     "permissions": [
            #         "create_message",
            #         "view_message",
            #         "edit_message",
            #         "delete_message",
            #     ]
            # },
            "service_catalog.support": {
                "permissions": [
                    "create_support",
                    "view_support",
                    "edit_support",
                    "delete_support",
                ]
            },
        },
    }
}
