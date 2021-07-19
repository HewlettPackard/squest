from django.urls import path

from resource_tracker.api.resource_group_api_views import ResourceGroupList, \
    ResourceGroupDetails, ResourceGroupResourceListCreate

urlpatterns = [
    path('resource_group/', ResourceGroupList.as_view(), name='api_resource_group_list'),
    path('resource_group/<int:pk>/', ResourceGroupDetails.as_view(), name='api_resource_group_details'),
    path('resource_group/<int:resource_group_id>/resources/', ResourceGroupResourceListCreate.as_view(),
         name='api_resource_group_resource_list_create'),
]
