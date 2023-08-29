import copy

from django.contrib.contenttypes.models import ContentType
from django.template.defaulttags import register


@register.filter(name='lookup')
def lookup(value, arg):
    return value[arg]


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter
def to_app_name(value):
    content_type = ContentType.objects.get_for_model(value)
    if content_type.model == "permission":
        return "profiles"
    return content_type.app_label


@register.simple_tag()
def has_perm(user, permission, object=None):
    return user.has_perm(permission, object)


@register.simple_tag()
def get_full_survey_user(squest_request, approval_step_state=None):
    return squest_request.full_survey_user(approval_step_state)


@register.simple_tag()
def who_can_approve_workflow(approval_step, scope):
    return approval_step.who_can_approve(scope)


@register.simple_tag()
def generate_sidebar(user):
    # data
    views_dict = {
        'Service catalog': [
            {
                'name': 'Service catalog',
                'view_name': 'service_catalog:service_catalog_list',
                'icon': 'fas fa-shopping-cart',
                'permission_required': 'service_catalog.list_service',
                'active': [
                    "service_catalog_list",
                    "portfolio_list", "portfolio_create", "portfolio_edit", "portfolio_delete",
                    "service_list", "service_create", "service_edit", "service_delete",
                    "operation_list", "operation_create", "operation_edit", "operation_delete", "operation_details",
                    "request_service", "create_operation_list", "operation_edit_survey"
                ]
            },
            {
                'name': 'Requests',
                'view_name': 'service_catalog:request_list',
                'icon': 'fas fa-tasks',
                'permission_required': 'service_catalog.list_request',
                'active': [
                    "request_list", "request_create", "request_edit", "request_delete",
                    "request_details", "request_cancel", "request_need_info", "request_re_submit", "request_reject",
                    "request_accept", "request_process", "request_archive", "request_unarchive", "request_approve",
                    "request_bulk_delete", "request_archived_list", "requestmessage_edit", "requestmessage_create"
                ]
            },
            {
                'name': 'Instances',
                'view_name': 'service_catalog:instance_list',
                'icon': 'fas fa-cubes',
                'permission_required': 'service_catalog.list_instance',
                'active': [
                    "instance_list", "instance_create", "instance_edit", "instance_delete", "instance_details",
                    "instance_bulk_delete", "instance_archive", "instance_unarchive", "instance_request_new_operation",
                    "support_create", "support_details", "support_close", "support_reopen", "supportmessage_edit"
                ]

            },
            {
                'name': 'Support',
                'view_name': 'service_catalog:support_list',
                'icon': 'fa fa-medkit',
                'permission_required': 'service_catalog.list_support',
                'active': [
                    "support_list"
                ]
            },
            {
                'name': 'Docs',
                'view_name': 'service_catalog:doc_list',
                'icon': 'fas fa-book',
                'permission_required': 'service_catalog.list_doc',
                'active': [
                    "doc_list", "doc_details"
                ]
            }

        ],
        'Resource tracking': [
            {
                'name': 'Attributes',
                'view_name': 'resource_tracker_v2:attributedefinition_list',
                'icon': 'fas fa-shapes',
                'permission_required': 'resource_tracker_v2.list_attributedefinition',
                'active': [
                    "attributedefinition_list", "attributedefinition_create", "attributedefinition_edit",
                    "attributedefinition_delete", "attributedefinition_details",
                ]
            },
            {
                'name': 'Resource groups',
                'view_name': 'resource_tracker_v2:resourcegroup_list',
                'icon': 'fas fa-object-group',
                'permission_required': 'resource_tracker_v2.list_resourcegroup',
                'active': [
                    "resourcegroup_list", "resourcegroup_create", "resourcegroup_edit",
                    "resourcegroup_delete", "resourcegroup_details", "resourcegroup_list_table",
                    "resourcegroup_list", "resourcegroup_create",
                    "transformer_list", "transformer_create", "transformer_edit", "transformer_delete",
                    "transformer_details",
                    "resource_list", "resource_create", "resource_edit", "resource_delete",
                    "resource_move", "resource_bulk_delete"
                ]
            },
            {
                'name': 'Graph',
                'view_name': 'resource_tracker_v2:resource_tracker_graph',
                'icon': 'fas fa-sitemap',
                'permission_required': 'resource_tracker_v2.list_resourcegroup',
                'active': [
                    "resource_tracker_graph"
                ]
            },
            {
                'name': 'Quota',
                'view_name': 'profiles:quota_list',
                'icon': 'fas fa-chart-pie',
                'permission_required': 'service_catalog.list_quota',
                'active': []
            },
        ],
        'Access': [
            {
                'name': 'Global permission',
                'view_name': 'profiles:globalpermission_rbac',
                'icon': 'fas fa-globe',
                'permission_required': 'profiles.can_view_globalpermission',
                'active': [
                    "globalpermission_rbac", "globalpermission_rbac_create", "globalpermission_rbac_delete"
                ]
            },
            {
                'name': 'Organization',
                'view_name': 'profiles:organization_list',
                'icon': 'fas fa-building',
                'permission_required': 'profiles.list_organization',
                'active': [
                    "organization_list", "organization_create", "organization_edit", "organization_delete",
                    "organization_details", "organization_rbac_create", "organization_rbac_delete"
                ]
            },
            {
                'name': 'Team',
                'view_name': 'profiles:team_list',
                'icon': 'fas fa-user',
                'permission_required': 'auth.list_user',
                'active': [
                    "team_list", "team_create", "team_edit", "team_delete",
                    "team_details", "team_rbac_create", "team_rbac_delete"
                ]
            },
            {
                'name': 'Users',
                'view_name': 'profiles:user_list',
                'icon': 'fas fa-user-friends',
                'permission_required': 'profiles.list_team',
                'active': [
                    "user_list", "user_details"
                ]
            },

        ],
        'Administration': [
            {
                'name': 'RHAAP/AWX',
                'view_name': 'service_catalog:towerserver_list',
                'icon': 'fas fa-chess-rook',
                'permission_required': 'service_catalog.list_towerserver',
                'active': [
                    "towerserver_list", "towerserver_create", "towerserver_edit", "towerserver_delete",
                    "towerserver_details", "jobtemplate_list", "jobtemplate_details", "jobtemplate_delete",
                    "job_template_compliancy"
                ]

            },
            {
                'name': 'Approval workflows',
                'view_name': 'service_catalog:approvalworkflow_list',
                'icon': 'fas fa-thumbs-up',
                'permission_required': 'service_catalog.list_approvalworkflow',
                'active': [
                    "approvalworkflow_list", "approvalworkflow_create", "approvalworkflow_edit", "approvalworkflow_delete",
                    "approvalworkflow_details", "approvalstep_create", "approvalstep_edit", "approvalstep_delete"
                ]

            },
            {
                'name': 'RBAC',
                'icon': 'fas fa-user-check',
                'active': [],
                'treeview_items': [
                    {
                        'name': 'Role',
                        'view_name': 'profiles:role_list',
                        'icon': 'fas fa-user-tie',
                        'permission_required': 'profiles.list_role',
                        'active': [
                            "role_list", "role_create", "role_edit", "role_delete", "role_details"
                        ]
                    },
                    {
                        'name': 'Permission',
                        'view_name': 'profiles:permission_list',
                        'icon': 'fas fa-unlock',
                        'permission_required': 'profiles.list_permission',
                        'active': [
                            "permission_list", "permission_create", "permission_edit", "permission_delete",
                            "approvalstep_permission_create"
                        ]
                    },
                    {
                        'name': 'Default permissions',
                        'view_name': 'profiles:globalpermission_default_permissions',
                        'icon': 'fas fa-check',
                        'permission_required': 'profiles.list_globalpermission',
                        'active': [
                            "globalpermission_default_permissions", "globalpermission_edit"
                        ]
                    }
                ],
            },
            {
                "name": "Extras",
                'icon': 'fas fa-stream',
                'active': [],
                'treeview_items': [
                    {
                        'name': 'Global hook',
                        'view_name': 'service_catalog:globalhook_list',
                        'icon': 'fas fa-file-code',
                        'permission_required': 'service_catalog.list_globalhook',
                        'active': ["globalhook_list", "globalhook_create", "globalhook_edit", "globalhook_delete"]
                    },
                    {
                        'name': 'Announcements',
                        'view_name': 'service_catalog:announcement_list',
                        'icon': 'fas fa-bullhorn',
                        'permission_required': 'service_catalog.list_announcement',
                        'active': ["announcement_list", "announcement_create", "announcement_edit", "announcement_delete"]
                    },
                    {
                        'name': 'Custom links',
                        'view_name': 'service_catalog:customlink_list',
                        'icon': 'fas fa-link',
                        'permission_required': 'service_catalog.list_customlink',
                        'active': ["customlink_list", "customlink_create", "customlink_edit", "customlink_delete"]
                    },
                ],
            }
        ],
    }
    # end data

    sidebar_menu = dict()
    for group_name, views in views_dict.items():
        is_group_visible = False
        group_items = list()

        for view in views:
            view_data_copy = copy.deepcopy(view)
            if "treeview_items" not in view:
                view_permission = view.get('permission_required', None)
                if (view_permission is None) or (view_permission is not None and user.has_perm(view_permission)):
                    is_group_visible = True
            else:
                view_data_copy["active"] = list()
                child_group = list()
                for child_view in view["treeview_items"]:
                    child_view_data_copy = copy.deepcopy(child_view)
                    view_data_copy["active"] += child_view_data_copy["active"]
                    view_permission = child_view.get('permission_required', None)
                    if (view_permission is None) or (view_permission is not None and user.has_perm(view_permission)):
                        is_group_visible = True
                    child_group.append(child_view_data_copy)
                view_data_copy["treeview_items"] = child_group

            group_items.append(view_data_copy)

        if is_group_visible:
            sidebar_menu[group_name] = group_items

    return sidebar_menu
