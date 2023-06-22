from django.conf.urls.static import static
from django.urls import path

from Squest import settings
from . import views
from .views.group_list_view import GroupListView
from .views.team_list_view import TeamListView
from .views.user_by_group_list_view import UserByGroupListView
from .views.user_list_view import UserListView

app_name = 'profiles'
urlpatterns = [
    # common URLs
    path('profile/', views.profile, name='profile'),
    path('profile/token/create/', views.token_create, name='token_create'),
    path('profile/token/<int:token_id>/generate/', views.token_generate, name='token_generate'),
    path('profile/token/<int:token_id>/edit/', views.token_edit, name='token_edit'),
    path('profile/token/<int:token_id>/delete/', views.token_delete, name='token_delete'),

    path('user/', UserListView.as_view(), name='user_list'),

    # group URLs
    path('group/<int:group_id>/users/', UserByGroupListView.as_view(), name='user_by_group_list'),
    path('group/<int:group_id>/users/update/', views.user_in_group_update, name='user_in_group_update'),
    path('group/<int:group_id>/users/remove/<int:user_id>/', views.user_in_group_remove, name='user_in_group_remove'),
    path('group/', GroupListView.as_view(), name='group_list'),
    path('group/create/', views.group_create, name='group_create'),
    path('group/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('group/<int:group_id>/delete/', views.group_delete, name='group_delete'),

    # billing group URLs
    path('billing-group/<int:billing_group_id>/users/update/', views.user_in_billing_group_update,
         name='user_in_billing_group_update'),
    path('billing-group/<int:billing_group_id>/users/remove/<int:user_id>/',
         views.user_in_billing_group_remove, name='user_in_billing_group_remove'),
    path('billing-group/', views.billing_group_list, name='billing_group_list'),
    path('billing-group/create/', views.billing_group_create, name='billing_group_create'),
    path('billing-group/<int:billing_group_id>/edit/', views.billing_group_edit, name='billing_group_edit'),
    path('billing-group/<int:billing_group_id>/delete/', views.billing_group_delete, name='billing_group_delete'),
    path('billing-group/<int:billing_group_id>/refresh_quota/', views.billing_group_refresh_quota, name='billing_group_refresh_quota'),

    # request notifications
    path('notification/request/switch/', views.request_notification_switch, name='request_notification_switch'),
    path('notification/notification_filter/request/create/', views.request_notification_create,
         name='request_notification_create'),
    path('notification/notification_filter/request/<int:request_notification_id>/delete/',
         views.request_notification_delete,
         name='request_notification_delete'),
    path('notification/notification_filter/request/<int:request_notification_id>/edit/',
         views.request_notification_edit,
         name='request_notification_edit'),

    # support notifications
    path('notification/support/switch/', views.support_notification_switch,
         name='support_notification_switch'),
    path('notification/notification_filter/support/create/', views.support_notification_create,
         name='support_notification_create'),
    path('notification/notification_filter/support/<int:support_notification_id>/delete/',
         views.support_notification_delete,
         name='support_notification_delete'),
    path('notification/notification_filter/support/<int:support_notification_id>/edit/',
         views.support_notification_edit,
         name='support_notification_edit'),


    # Scope
    path('scope/<int:scope_id>/role/<int:pk>/delete/', views.scope_role_delete, name="scope_role_delete"),

    # Organization
    path('organization/', views.OrganizationListView.as_view(), name="organization_list"),
    path('organization/create/', views.OrganizationCreateView.as_view(), name="organization_create"),
    path('organization/<int:pk>/edit/', views.OrganizationEditView.as_view(), name="organization_edit"),
    path('organization/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name="organization_delete"),
    path('organization/<int:pk>/', views.OrganizationDetailView.as_view(), name="organization_details"),
    path('organization/<int:pk>/role/create/', views.organization_role_create, name="organization_role_create"),
    path('organization/<int:pk>/rbac/create/', views.organization_rbac_create, name="organization_rbac_create"),
    path('organization/<int:scope_id>/rbac/<int:rbac_id>/user/<int:user_id>/delete/', views.organization_rbac_delete, name="organization_rbac_delete"),
    path('organization/<int:pk>/team/create/', views.OrganizationTeamCreateView.as_view(), name="organization_team_create"),

    # User Role Binding URLs
    path('role/ajax/get-users-with-role/', views.ajax_get_users_with_role, name='get_users_with_role'),
    path('role/ajax/get-teams-with-role/', views.ajax_get_teams_with_role, name='get_teams_with_role'),

    # Team
    path('team/', views.TeamListView.as_view(), name="team_list"),
    path('team/create/', views.TeamCreateView.as_view(), name="team_create"),
    path('team/<int:pk>/edit', views.TeamEditView.as_view(), name="team_edit"),
    path('team/<int:pk>/delete', views.TeamDeleteView.as_view(), name="team_delete"),
    path('team/<int:pk>/', views.TeamDetailView.as_view(), name="team_details"),
    path('team/<int:pk>/role/create/', views.team_role_create, name="team_role_create"),
    path('team/<int:pk>/rbac/create/', views.team_rbac_create, name="team_rbac_create"),
    path('team/<int:scope_id>/rbac/<int:rbac_id>/user/<int:user_id>/delete/', views.team_rbac_delete, name="team_rbac_delete"),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
