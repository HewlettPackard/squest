from django.urls import path
from profiles.api.views.billing_group_api_views import BillingGroupListCreate, BillingGroupDetails
from profiles.api.views.user_api_views import UserListCreate, UserDetails

urlpatterns = [
    path('user/', UserListCreate.as_view(), name='api_user_list_create'),
    path('user/<int:pk>/', UserDetails.as_view(), name='api_user_details'),
    path('billing-group/', BillingGroupListCreate.as_view(), name='api_billing_group_list_create'),
    path('billing-group/<int:pk>/', BillingGroupDetails.as_view(), name='api_billing_group_details'),
]
