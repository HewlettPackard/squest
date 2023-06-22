from django.conf.urls.static import static
from django.urls import path

from Squest import settings
from . import views

app_name = 'profiles'

urlpatterns = [
    # common URLs
    path('profile/', views.profile, name='profile'),
    path('profile/token/create/', views.token_create, name='token_create'),
    path('profile/token/<int:token_id>/generate/', views.token_generate, name='token_generate'),
    path('profile/token/<int:token_id>/edit/', views.token_edit, name='token_edit'),
    path('profile/token/<int:token_id>/delete/', views.token_delete, name='token_delete'),

    path('user/', views.UserListView.as_view(), name='user_list'),
    path('user/<int:pk>/', views.UserDetailsView.as_view(), name='user_details'),

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


    # Team
    path('team/', views.TeamListView.as_view(), name="team_list"),
    path('team/create/', views.TeamCreateView.as_view(), name="team_create"),
    path('team/<int:pk>/edit', views.TeamEditView.as_view(), name="team_edit"),
    path('team/<int:pk>/delete', views.TeamDeleteView.as_view(), name="team_delete"),
    path('team/<int:pk>/', views.TeamDetailView.as_view(), name="team_details"),
    path('team/<int:pk>/role/create/', views.team_role_create, name="team_role_create"),
    path('team/<int:pk>/rbac/create/', views.team_rbac_create, name="team_rbac_create"),
    path('team/<int:scope_id>/rbac/<int:rbac_id>/user/<int:user_id>/delete/', views.team_rbac_delete, name="team_rbac_delete"),

    # Role
    path('role/', views.RoleListView.as_view(), name="role_list"),
    path('role/create/', views.RoleCreateView.as_view(), name="role_create"),
    path('role/<int:pk>/edit/', views.RoleEditView.as_view(), name="role_edit"),
    path('role/<int:pk>/delete/', views.RoleDeleteView.as_view(), name="role_delete"),
    path('role/<int:pk>/', views.RoleDetailView.as_view(), name="role_details"),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
