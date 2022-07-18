from django.urls import path
from profiles.api.views.billing_group_api_views import BillingGroupListCreate, BillingGroupDetails
from profiles.api.views.notification_filter import NotificationFilterListCreate, NotificationFilterDetails
from profiles.api.views.quota_api_views import QuotaListCreate, QuotaDetails
from profiles.api.views.quota_binding_api_views import QuotaBindingDetails, QuotaBindingListCreate
from profiles.api.views.user_api_views import UserListCreate, UserDetails

urlpatterns = [
    path('user/', UserListCreate.as_view(), name='api_user_list_create'),
    path('user/<int:pk>/', UserDetails.as_view(), name='api_user_details'),
    path('billing-group/', BillingGroupListCreate.as_view(), name='api_billing_group_list_create'),
    path('billing-group/<int:pk>/', BillingGroupDetails.as_view(), name='api_billing_group_details'),
    path('quota/', QuotaListCreate.as_view(), name='api_quota_list_create'),
    path('quota/<int:pk>/', QuotaDetails.as_view(), name='api_quota_details'),
    path('quota-binding/', QuotaBindingListCreate.as_view(), name='api_quota_binding_list_create'),
    path('quota-binding/<int:pk>/', QuotaBindingDetails.as_view(), name='api_quota_binding_details'),
    path('notification-filter/', NotificationFilterListCreate.as_view(), name='api_notification_filter_list_create'),
    path('notification-filter/<int:pk>/', NotificationFilterDetails.as_view(), name='api_notification_filter_details'),
]
