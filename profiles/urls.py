from django.conf.urls.static import static
from django.urls import path

from Squest import settings
from . import views

app_name = 'profiles'

urlpatterns = [
    # Personal URLs ####################################################################################################

    # profile URLs
    path('profile/', views.profile, name='profile'),
    path('profile/theme-switch/', views.dark_light_theme_switch, name='dark_light_theme_switch'),
    path('profile/token/create/', views.token_create, name='token_create'),
    path('profile/token/<int:token_id>/generate/', views.token_generate, name='token_generate'),
    path('profile/token/<int:token_id>/edit/', views.token_edit, name='token_edit'),
    path('profile/token/<int:token_id>/delete/', views.token_delete, name='token_delete'),

    # request notifications
    path('notification/request/switch/', views.requestnotification_switch, name='requestnotification_switch'),
    path('notification/notification_filter/request/create/', views.RequestNotificationCreateView.as_view(),
         name='requestnotification_create'),
    path('notification/notification_filter/request/<int:pk>/delete/',
         views.RequestNotificationDeleteView.as_view(),
         name='requestnotification_delete'),
    path('notification/notification_filter/request/<int:pk>/edit/',
         views.RequestNotificationEditView.as_view(),
         name='requestnotification_edit'),

    # instance notifications
    path('notification/instance/switch/', views.instancenotification_switch,
         name='instancenotification_switch'),
    path('notification/notification_filter/instance/create/', views.InstanceNotificationCreateView.as_view(),
         name='instancenotification_create'),
    path('notification/notification_filter/instance/<int:pk>/delete/',
         views.InstanceNotificationDeleteView.as_view(),
         name='instancenotification_delete'),
    path('notification/notification_filter/instance/<int:pk>/edit/',
         views.InstanceNotificationEditView.as_view(),
         name='instancenotification_edit'),

    ####################################################################################################################

    # User
    path('user/', views.UserListView.as_view(), name='user_list'),
    path('user/<int:pk>/', views.UserDetailsView.as_view(), name='user_details'),

    # Global Permission
    path('global-permission/', views.GlobalPermissionRBACView.as_view(), name="globalpermission_rbac"),
    path('global-permission/default-permission/', views.GlobalPermissionDefaultPermissionView.as_view(), name="globalpermission_default_permissions"),
    path('global-permission/edit/', views.GlobalPermissionEditView.as_view(), name="globalpermission_edit"),
    path('global-permission/<int:scope_id>/role/create/', views.ScopeRBACCreateView.as_view(), name="globalpermission_rbac_create"),
    path('global-permission/<int:pk>/role/<int:role_id>/user/<int:user_id>/delete/', views.ScopeRBACDeleteView.as_view(), name="globalpermission_rbac_delete"),

    # Organization
    path('organization/', views.OrganizationListView.as_view(), name="organization_list"),
    path('organization/create/', views.OrganizationCreateView.as_view(), name="organization_create"),
    path('organization/<int:pk>/edit/', views.OrganizationEditView.as_view(), name="organization_edit"),
    path('organization/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name="organization_delete"),
    path('organization/<int:pk>/', views.OrganizationDetailView.as_view(), name="organization_details"),
    path('organization/<int:scope_id>/role/create/', views.ScopeRBACCreateView.as_view(), name="organization_rbac_create"),
    path('organization/<int:pk>/role/<int:role_id>/user/<int:user_id>/delete/', views.ScopeRBACDeleteView.as_view(), name="organization_rbac_delete"),

    # Team
    path('team/', views.TeamListView.as_view(), name="team_list"),
    path('team/create/', views.TeamCreateView.as_view(), name="team_create"),
    path('team/<int:pk>/edit/', views.TeamEditView.as_view(), name="team_edit"),
    path('team/<int:pk>/delete/', views.TeamDeleteView.as_view(), name="team_delete"),
    path('team/<int:pk>/', views.TeamDetailView.as_view(), name="team_details"),
    path('team/<int:scope_id>/role/create/', views.ScopeRBACCreateView.as_view(), name="team_rbac_create"),
    path('team/<int:pk>/role/<int:role_id>/user/<int:user_id>/delete/', views.ScopeRBACDeleteView.as_view(), name="team_rbac_delete"),

    # Permission
    path('permission/', views.PermissionListView.as_view(), name="permission_list"),
    path('permission/create/', views.PermissionCreateView.as_view(), name="permission_create"),
    path('permission/<int:pk>/edit/', views.PermissionEditView.as_view(), name="permission_edit"),
    path('permission/<int:pk>/delete/', views.PermissionDeleteView.as_view(), name="permission_delete"),
    # Specific permission
    path('permission/create/approvalstep', views.ApprovalStepPermissionCreateView.as_view(), name="approvalstep_permission_create"),

    # Role
    path('role/', views.RoleListView.as_view(), name="role_list"),
    path('role/create/', views.RoleCreateView.as_view(), name="role_create"),
    path('role/<int:pk>/edit/', views.RoleEditView.as_view(), name="role_edit"),
    path('role/<int:pk>/delete/', views.RoleDeleteView.as_view(), name="role_delete"),
    path('role/<int:pk>/', views.RoleDetailView.as_view(), name="role_details"),

    # Quota
    path('quota/', views.QuotaListView.as_view(), name="quota_list"),
    path('quota/<int:pk>/delete/', views.QuotaDeleteView.as_view(), name="quota_delete"),
    path('organization/<int:scope_id>/quota/', views.QuotaEditView.as_view(),
         name="organization_quota_edit"),
    path('team/<int:scope_id>/quota/', views.QuotaEditView.as_view(),
         name="team_quota_edit"),
    path('team/<int:scope_id>/quota/<int:quota_id>/', views.QuotaDetailsView.as_view(),
         name="quota_details")

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
