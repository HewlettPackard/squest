from django.urls import path

from profiles.api.views import *

urlpatterns = [
    # User
    path('user/', UserListCreate.as_view(), name='api_user_list_create'),
    path('user/<int:pk>/', UserDetails.as_view(), name='api_user_details'),

    # Request notification
    path('notification-filter/request/', RequestNotificationFilterListCreate.as_view(), name='api_requestnotification_list_create'),
    path('notification-filter/request/<int:pk>/', RequestNotificationFilterDetails.as_view(), name='api_requestnotification_details'),

    # Instance notification
    path('notification-filter/instance/', InstanceNotificationFilterListCreate.as_view(), name='api_instancenotification_list_create'),
    path('notification-filter/instance/<int:pk>/', InstanceNotificationFilterDetails.as_view(), name='api_instancenotification_details'),

    # Global scope
    path('global-scope/', GlobalScopeDetails.as_view(), name='api_globalscope_details'),
    path('global-scope/<int:scope_id>/role/create/', ScopeRBACCreate.as_view(), name="api_globalscope_rbac_create"),
    path('global-scope/<int:scope_id>/role/<int:role_id>/user/<int:user_id>/delete/', ScopeRBACDelete.as_view(), name="api_globalscope_rbac_delete"),
    path('global-scope/<int:scope_id>/user/<int:user_id>/delete/', ScopeUserDelete.as_view(), name="api_globalscope_user_delete"),

    # Scope
    path('scope/<int:pk>/', RedirectScopeDetails.as_view(), name="api_scope_details"),

    # Organization
    path('organization/', OrganizationListCreate.as_view(), name='api_organization_list_create'),
    path('organization/<int:pk>/', OrganizationDetails.as_view(), name='api_organization_details'),
    path('organization/<int:scope_id>/role/create/', ScopeRBACCreate.as_view(), name="api_organization_rbac_create"),
    path('organization/<int:scope_id>/role/<int:role_id>/user/<int:user_id>/delete/', ScopeRBACDelete.as_view(), name="api_organization_rbac_delete"),
    path('organization/<int:scope_id>/user/<int:user_id>/delete/', ScopeUserDelete.as_view(), name="api_organization_user_delete"),

    # Team
    path('team/', TeamListCreate.as_view(), name='api_team_list_create'),
    path('team/<int:pk>/', TeamDetails.as_view(), name='api_team_details'),
    path('team/<int:scope_id>/role/create/', ScopeRBACCreate.as_view(), name="api_team_rbac_create"),
    path('team/<int:scope_id>/role/<int:role_id>/user/<int:user_id>/delete/', ScopeRBACDelete.as_view(), name="api_team_rbac_delete"),
    path('team/<int:scope_id>/user/<int:user_id>/delete/', ScopeUserDelete.as_view(), name="api_team_user_delete"),

    # Role
    path('role/', RoleListCreate.as_view(), name='api_role_list_create'),
    path('role/<int:pk>/', RoleDetails.as_view(), name='api_role_details'),

    # Permission
    path('permission/', PermissionListCreate.as_view(), name='api_permission_list_create'),
    path('permission/<int:pk>/', PermissionDetails.as_view(), name='api_permission_details'),

    # Quota
    path('quota/<int:pk>/', QuotaDetails.as_view(), name="api_quota_details"),
    path('quota/', QuotaListCreate.as_view(), name="api_quota_list_create"),


]
