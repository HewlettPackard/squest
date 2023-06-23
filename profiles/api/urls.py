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

]
