from django.urls import path

from resource_tracker.api.resource_group_api_views import ResourceGroupList, \
    ResourceGroupDetails, AttributeDefinitionList, AttributeDefinitionDetails, TextAttributeDefinitionList, \
    TextAttributeDefinitionDetails
from resource_tracker.api.resource_api_view import ResourceListCreate, ResourceGetDelete
from resource_tracker.api.resource_pool_api_views import ResourcePoolList, ResourcePoolDetails, \
    PoolAttributeDefinitionList, PoolAttributeDefinitionDetails

urlpatterns = [
    # resource group
    path('resource_group/', ResourceGroupList.as_view(), name='api_resource_group_list_create'),
    path('resource_group/<int:pk>/', ResourceGroupDetails.as_view(), name='api_resource_group_details'),
    path('resource_group/<int:pk>/attribute_definitions/', AttributeDefinitionList.as_view(),
         name='api_attribute_definition_list_create'),
    path('resource_group/<int:pk>/attribute_definitions/<int:attribute_definition_id>/',
         AttributeDefinitionDetails.as_view(),
         name='api_attribute_definition_retrieve_update_delete'),
    path('resource_group/<int:pk>/text_attribute_definitions/', TextAttributeDefinitionList.as_view(),
         name='api_text_attribute_definition_list_create'),
    path('resource_group/<int:pk>/text_attribute_definitions/<int:text_attribute_definition_id>/',
         TextAttributeDefinitionDetails.as_view(),
         name='api_text_attribute_definition_retrieve_update_delete'),
    path('resource_group/<int:resource_group_id>/resources/', ResourceListCreate.as_view(),
         name='api_resource_list_create'),
    path('resource_group/<int:resource_group_id>/resources/<int:pk>/', ResourceGetDelete.as_view(),
         name='api_resource_retrieve_delete'),
    # resource pool
    path('resource_pool/', ResourcePoolList.as_view(), name='api_resource_pool_list_create'),
    path('resource_pool/<int:pk>/', ResourcePoolDetails.as_view(), name='api_resource_pool_details'),
    path('resource_pool/<int:pk>/attribute_definitions/', PoolAttributeDefinitionList.as_view(),
         name='api_resource_pool_attribute_definition_list_create'),
    path('resource_pool/<int:pk>/attribute_definitions/<int:attribute_definition_id>/',
         PoolAttributeDefinitionDetails.as_view(),
         name='api_resource_pool_attribute_definition_retrieve_update_delete')
]
