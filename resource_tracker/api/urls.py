from django.urls import path

from resource_tracker.api.resource_group_api_views import ResourceGroupList, \
    ResourceGroupDetails, AttributeDefinitionList, AttributeDefinitionDetails
from resource_tracker.api.resource_api_view import ResourceListCreate, ResourceGetDelete

urlpatterns = [
    path('resource_group/', ResourceGroupList.as_view(), name='api_resource_group_list_create'),
    path('resource_group/<int:pk>/', ResourceGroupDetails.as_view(), name='api_resource_group_details'),
    path('resource_group/<int:pk>/attribute_definitions/', AttributeDefinitionList.as_view(),
         name='api_attribute_definition_list_create'),
    path('resource_group/<int:pk>/attribute_definitions/<int:attribute_definition_id>/',
         AttributeDefinitionDetails.as_view(),
         name='api_attribute_definition_retrieve_update_delete'),
    path('resource_group/<int:resource_group_id>/resources/', ResourceListCreate.as_view(),
         name='api_resource_list_create'),
    path('resource_group/<int:resource_group_id>/resources/<int:resource_id>/', ResourceGetDelete.as_view(),
         name='api_resource_retrieve_delete'),
]
