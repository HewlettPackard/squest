from django.urls import path

from resource_tracker_v2 import views

app_name = 'resource_tracker'

urlpatterns = [
    # attributes
    path('attributes/', views.AttributeDefinitionListView.as_view(), name='attribute_definition_list'),
    path('attributes/create/', views.AttributeDefinitionCreateView.as_view(), name='attribute_definition_create'),
    path('attributes/<int:attribute_definition_id>/edit/', views.AttributeDefinitionEditView.as_view(),
         name='attribute_definition_edit'),
    path('attributes/<int:attribute_definition_id>/delete/', views.AttributeDefinitionDeleteView.as_view(),
         name='attribute_definition_delete'),

    # resource group
    path('resource_group/', views.ResourceGroupListView.as_view(), name='resource_group_list'),
    path('resource_group/create/', views.ResourceGroupCreateView.as_view(), name='resource_group_create'),
    path('resource_group/<int:resource_group_id>/edit/', views.ResourceGroupEditView.as_view(),
         name='resource_group_edit'),
    path('resource_group/<int:resource_group_id>/delete/', views.ResourceGroupDeleteView.as_view(),
         name='resource_group_delete'),

    # resource group attributes
    path('resource_group/<int:resource_group_id>/attributes/', views.TransformerListView.as_view(),
         name='resource_group_attribute_list'),
    path('resource_group/<int:resource_group_id>/attributes/create/',
         views.TransformerCreateView.as_view(),
         name='resource_group_attribute_create'),
    path('resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/edit/',
         views.TransformerEditView.as_view(),
         name='resource_group_attribute_edit'),
    path('resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/delete/',
         views.TransformerDeleteView.as_view(),
         name='resource_group_attribute_delete'),
    path('tool/resource_group/load-resource-group-attribute/', views.ajax_load_attribute,
         name='ajax_load_attribute'),
    path('resource_group/<int:resource_group_id>/resources/', views.ResourceListView.as_view(),
         name='resource_group_resource_list'),
    path('resource_group/<int:resource_group_id>/resources/create/', views.ResourceCreateView.as_view(),
         name='resource_group_resource_create'),
    path('resource_group/<int:resource_group_id>/resources/<int:resource_id>/edit/', views.ResourceEditView.as_view(),
         name='resource_group_resource_edit'),
    path('resource_group/<int:resource_group_id>/resources/<int:resource_id>/delete/', views.ResourceDeleteView.as_view(),
         name='resource_group_resource_delete'),
    path('resource_group/<int:resource_group_id>/resources/delete-confirm/',
         views.resource_group_resource_bulk_delete_confirm,
         name='resource_group_resource_bulk_delete_confirm'),
    path('resource_group/<int:resource_group_id>/resources/delete-force/',
         views.resource_group_resource_bulk_delete,
         name='resource_group_resource_bulk_delete'),

    # graph
    path('resource_tracker_graph/', views.resource_tracker_graph, name='resource_tracker_graph'),
]
