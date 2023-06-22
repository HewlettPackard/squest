from django.urls import path
from profiles.api.views.billing_group_api_views import BillingGroupListCreate, BillingGroupDetails
from profiles.api.views.request_notification_filter import RequestNotificationFilterListCreate, RequestNotificationFilterDetails
from profiles.api.views.support_notification_filter import SupportNotificationFilterListCreate, \
    SupportNotificationFilterDetails
from profiles.api.views.user_api_views import UserListCreate, UserDetails

urlpatterns = [
    path('user/', UserListCreate.as_view(), name='api_user_list_create'),
    path('user/<int:pk>/', UserDetails.as_view(), name='api_user_details'),
    path('billing-group/', BillingGroupListCreate.as_view(), name='api_billing_group_list_create'),
    path('billing-group/<int:pk>/', BillingGroupDetails.as_view(), name='api_billing_group_details'),
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

]
