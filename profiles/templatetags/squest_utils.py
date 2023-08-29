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
                'permission_required': 'service_catalog.list_service'
            },
            {
                'name': 'Requests',
                'view_name': 'service_catalog:request_list',
                'icon': 'fas fa-tasks',
                'permission_required': 'service_catalog.list_request'
            },
            {
                'name': 'Instances',
                'view_name': 'service_catalog:instance_list',
                'icon': 'fas fa-cubes',
                'permission_required': 'service_catalog.list_instance'

            },
            {
                'name': 'Support',
                'view_name': 'service_catalog:support_list',
                'icon': 'fa fa-medkit',
                'permission_required': 'service_catalog.list_support'
            },
            {
                'name': 'Docs',
                'view_name': 'service_catalog:doc_list',
                'icon': 'fas fa-book',
                'permission_required': 'service_catalog.list_doc'
            }

        ],
        'Resource tracking': [
            {
                'name': 'Attributes',
                'view_name': 'resource_tracker_v2:attributedefinition_list',
                'icon': 'fas fa-shapes',
                'permission_required': 'resource_tracker_v2.list_attributedefinition'
            },
            {
                'name': 'Resource groups',
                'view_name': 'resource_tracker_v2:resourcegroup_list',
                'icon': 'fas fa-object-group',
                'permission_required': 'resource_tracker_v2.list_resourcegroup'
            },
            {
                'name': 'Graph',
                'view_name': 'resource_tracker_v2:resource_tracker_graph',
                'icon': 'fas fa-sitemap',
                'permission_required': 'resource_tracker_v2.list_resourcegroup'
            },
            {
                'name': 'Quota',
                'view_name': 'profiles:quota_list',
                'icon': 'fas fa-chart-pie',
                'permission_required': 'service_catalog.list_quota'
            },
        ],
        'Access': [
            {
                'name': 'Global permission',
                'view_name': 'profiles:globalpermission_rbac',
                'icon': 'fas fa-globe',
                'permission_required': 'profiles.can_view_globalpermission'
            },
            {
                'name': 'Organization',
                'view_name': 'profiles:organization_list',
                'icon': 'fas fa-building',
                'permission_required': 'profiles.list_organization'
            },
            {
                'name': 'Team',
                'view_name': 'profiles:team_list',
                'icon': 'fas fa-user',
                'permission_required': 'auth.list_user'
            },
            {
                'name': 'Users',
                'view_name': 'profiles:user_list',
                'icon': 'fas fa-user-friends',
                'permission_required': 'profiles.list_team'
            },

        ],
        'Administration': [
            {
                'name': 'RHAAP/AWX',
                'view_name': 'service_catalog:towerserver_list',
                'icon': 'fas fa-chess-rook',
                'permission_required': 'service_catalog.list_towerserver'

            },
            {
                'name': 'Approval workflows',
                'view_name': 'service_catalog:approvalworkflow_list',
                'icon': 'fas fa-thumbs-up',
                'permission_required': 'service_catalog.list_approvalworkflow'

            },
            {
                'name': 'RBAC',
                'icon': 'fas fa-user-check',
                'treeview_items': [
                    {
                        'name': 'Role',
                        'view_name': 'profiles:role_list',
                        'icon': 'fas fa-user-tie',
                        'permission_required': 'profiles.list_role'
                    },
                    {
                        'name': 'Permission',
                        'view_name': 'profiles:permission_list',
                        'icon': 'fas fa-unlock',
                        'permission_required': 'profiles.list_permission'
                    },
                    {
                        'name': 'Default permissions',
                        'view_name': 'profiles:globalpermission_default_permissions',
                        'icon': 'fas fa-check',
                        'permission_required': 'profiles.list_globalpermission'
                    }
                ],
            },
            {
                "name": "Extras",
                'icon': 'fas fa-stream',
                'treeview_items': [
                    {
                        'name': 'Global hook',
                        'view_name': 'service_catalog:globalhook_list',
                        'icon': 'fas fa-file-code',
                        'permission_required': 'service_catalog:list_globalhook'
                    },
                    {
                        'name': 'Announcements',
                        'view_name': 'service_catalog:announcement_list',
                        'icon': 'fas fa-bullhorn',
                        'permission_required': 'service_catalog:list_announcement'
                    },
                    {
                        'name': 'Custom links',
                        'view_name': 'service_catalog:customlink_list',
                        'icon': 'fas fa-link',
                        'permission_required': 'service_catalog:list_customlink'
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
                view_data_copy["view_name_short"] = [view["view_name"].split(':')[1]]
                view_permission = view.get('permission_required', None)
                if (view_permission is None) or (view_permission is not None and user.has_perm(view_permission)):
                    is_group_visible = True
            else:
                view_data_copy["view_name_short"] = list()
                child_group = list()
                for child_view in view["treeview_items"]:
                    child_view_data_copy = copy.deepcopy(child_view)
                    child_view_data_copy["view_name_short"] = child_view_data_copy["view_name"].split(':')[1]
                    view_data_copy["view_name_short"].append(child_view_data_copy["view_name_short"])
                    view_permission = child_view.get('permission_required', None)
                    if (view_permission is None) or (view_permission is not None and user.has_perm(view_permission)):
                        is_group_visible = True
                    child_group.append(child_view_data_copy)
                    view_data_copy["treeview_items"] = child_group

            group_items.append(view_data_copy)

        if is_group_visible:
            sidebar_menu[group_name] = group_items

    return sidebar_menu
