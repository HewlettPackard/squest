from django.urls import path

from resource_tracker_v2.api.views.attribute_definition_api_views import AttributeDefinitionList, \
    AttributeDefinitionDetails
from resource_tracker_v2.api.views.resource_api_view import ResourceListCreate, ResourceDetails
from resource_tracker_v2.api.views.resource_group_api_views import ResourceGroupList, ResourceGroupDetails
from resource_tracker_v2.api.views.transformer_api_views import TransformerListCreate, TransformerDetails

urlpatterns = [
    # attribute definition
    path('attributes/', AttributeDefinitionList.as_view(), name='api_attributedefinition_list_create'),
    path('attributes/<int:pk>/', AttributeDefinitionDetails.as_view(), name='api_attributedefinition_details'),

    # resource group
    path('resource_group/', ResourceGroupList.as_view(), name='api_resourcegroup_list_create'),
    path('resource_group/<int:pk>/', ResourceGroupDetails.as_view(), name='api_resourcegroup_details'),

    # resource
    path('resource_group/<int:resource_group_id>/resources/', ResourceListCreate.as_view(),
         name='api_resource_list_create'),
    path('resource_group/<int:resource_group_id>/resources/<int:pk>/', ResourceDetails.as_view(),
         name='api_resource_details'),
    # path('resource_group/<int:resource_group_id>/resources/<int:pk>/move/', ResourceMove.as_view(),
    #      name='api_resource_move'),

    # transformer
    path('resource_group/<int:resource_group_id>/attributes/', TransformerListCreate.as_view(),
         name='api_transformer_list_create'),
    path('resource_group/<int:resource_group_id>/attributes/<int:pk>/', TransformerDetails.as_view(),
         name='api_transformer_details'),

]
