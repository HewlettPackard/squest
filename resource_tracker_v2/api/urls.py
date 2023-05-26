from django.urls import path

from resource_tracker_v2.api.views.resource_group_api_views import ResourceGroupList, ResourceGroupDetails

urlpatterns = [
    # resource group
    path('resource_group/', ResourceGroupList.as_view(), name='api_resource_group_list_create'),
    path('resource_group/<int:pk>/', ResourceGroupDetails.as_view(), name='api_resource_group_details'),
]
