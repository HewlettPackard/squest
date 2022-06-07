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
                    "delete_instance",
                    "request_operation_on_instance",
                    "request_support_on_instance",
                    "view_instance"
                ]
            },
            "Operator": {
                "description": "An operator can request for operations on the instance",
                "permissions": [
                    "request_operation_on_instance",
                    "request_support_on_instance",
                    "view_instance"
                ]
            },
            "Reader": {
                "description": "A reader can access the instance",
                "permissions": [
                    "view_instance"
                ]
            }
        },
    "service_catalog.request":
        {
            "Admin": {
                "description": "An administrator of the request can manage it",
                "permissions": [
                    "change_request",
                    "delete_request",
                    "cancel_request",
                    "comment_request",
                    "view_request"
                ]
            },
            "Operator": {
                "description": "An operator can request for operations on the request",
                "permissions": [
                    "comment_request",
                    "cancel_request",
                    "view_request"
                ]
            },
            "Reader": {
                "description": "A reader can access the request",
                "permissions": [
                    "view_request"
                ]
            }
        },
    "service_catalog.approvalstep":
        {
            "Approver": {
                "description": "An approver of the approval step can approve requests related to it.",
                "permissions": [
                    "change_approvalstep",
                    "delete_approvalstep",
                    "view_approvalstep",
                    "approve_request_approvalstep",
                ]
            }
        }
}
