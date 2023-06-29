from django.urls import path
from profiles.api.views import *

urlpatterns = [
    # User
    path('user/', UserListCreate.as_view(), name='api_user_list_create'),
    path('user/<int:pk>/', UserDetails.as_view(), name='api_user_details'),

    # Notification
    path('notification-filter/request/', RequestNotificationFilterListCreate.as_view(),
         name='api_request_notification_filter_list_create'),
    path('notification-filter/request/<int:pk>/', RequestNotificationFilterDetails.as_view(),
         name='api_request_notification_filter_details'),
    path('notification-filter/support/', SupportNotificationFilterListCreate.as_view(),
         name='api_support_notification_filter_list_create'),
    path('notification-filter/support/<int:pk>/', SupportNotificationFilterDetails.as_view(),
         name='api_support_notification_filter_details'),

    # Scope
    path('global-permission/<int:scope_id>/role/create/', ScopeRBACCreate.as_view(), name="api_globalpermission_rbac_create"),
    path('global-permission/<int:scope_id>/role/<int:role_id>/user/<int:user_id>/delete/', ScopeRBACDelete.as_view(), name="api_globalpermission_rbac_delete"),
    path('organization/<int:scope_id>/role/create/', ScopeRBACCreate.as_view(), name="api_organization_rbac_create"),
    path('organization/<int:scope_id>/role/<int:role_id>/user/<int:user_id>/delete/', ScopeRBACDelete.as_view(), name="api_organization_rbac_delete"),
    path('team/<int:scope_id>/role/create/', ScopeRBACCreate.as_view(), name="api_team_rbac_create"),
    path('team/<int:scope_id>/role/<int:role_id>/user/<int:user_id>/delete/', ScopeRBACDelete.as_view(), name="api_team_rbac_delete"),

    # Global Permission
    path('global-permission/', GlobalPermissionDetails.as_view(), name='api_organization_details'),

    # Organization
    path('organization/', OrganizationListCreate.as_view(), name='api_organization_list_create'),
    path('organization/<int:pk>/', OrganizationDetails.as_view(), name='api_organization_details'),

    # Team
    path('organization/<int:organization_id>/team/', OrganizationTeamListCreate.as_view(), name='api_team_list_create'),
    path('organization/<int:organization_id>/team/<int:pk>/', OrganizationTeamDetails.as_view(), name='api_team_details'),
    path('team/', TeamListCreate.as_view(), name='api_team_list_create'),
    path('team/<int:pk>/', TeamDetails.as_view(), name='api_team_details'),

    # Role
    path('role/', RoleListCreate.as_view(), name='api_role_list_create'),
    path('role/<int:pk>/', RoleDetails.as_view(), name='api_role_details'),

    # RBAC
    path('scope/', RoleListCreate.as_view(), name='api_role_list_create'),
    path('role/<int:pk>/', RoleDetails.as_view(), name='api_role_details'),

    # Permission
    path('permission/', PermissionList.as_view(), name='api_permission_list'),
    path('permission/<int:pk>/', PermissionDetails.as_view(), name='api_permission_details'),

    # Quota
    path('organization/<int:scope_id>/quota/', QuotaListCreateView.as_view(),
         name="quota_org_list_create"),
    path('team/<int:scope_id>/quota/', QuotaListCreateView.as_view(),
         name="quota_team_list_create"),
    path('organization/<int:scope_id>/quota/<int:pk>/', QuotaDetails.as_view(),
         name="quota_org_details"),
    path('team/<int:scope_id>/quota/<int:pk>/', QuotaDetails.as_view(),
         name="quota_team_details"),

]
