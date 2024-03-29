from django.urls import path

from resource_tracker_v2 import views

app_name = 'resource_tracker_v2'

urlpatterns = [
    # Attribute definition CRUD
    path('attribute/', views.AttributeDefinitionListView.as_view(), name='attributedefinition_list'),
    path('attribute/create/', views.AttributeDefinitionCreateView.as_view(), name='attributedefinition_create'),
    path('attribute/<int:pk>/', views.AttributeDefinitionDetailView.as_view(), name='attributedefinition_details'),
    path('attribute/<int:pk>/edit/', views.AttributeDefinitionEditView.as_view(), name='attributedefinition_edit'),
    path('attribute/<int:pk>/delete/', views.AttributeDefinitionDeleteView.as_view(), name='attributedefinition_delete'),

    # Resource group CRUD
    path('resource-group/', views.ResourceGroupListView.as_view(), name='resourcegroup_list'),
    path('resource-group/table/', views.ResourceGroupListViewCSV.as_view(), name='resourcegroup_list_table'),
    path('resource-group/create/', views.ResourceGroupCreateView.as_view(), name='resourcegroup_create'),
    path('resource-group/<int:pk>/', views.ResourceGroupDetailView.as_view(), name='resourcegroup_details'),
    path('resource-group/<int:pk>/edit/', views.ResourceGroupEditView.as_view(), name='resourcegroup_edit'),
    path('resource-group/<int:pk>/delete/', views.ResourceGroupDeleteView.as_view(), name='resourcegroup_delete'),
    # Graph
    path('graph/', views.resource_tracker_graph, name='resource_tracker_graph'),

    # Transformer CRUD
    path('resource-group/<int:resource_group_id>/attribute/', views.TransformerListView.as_view(), name='transformer_list'),
    path('resource-group/<int:resource_group_id>/attribute/create/', views.TransformerCreateView.as_view(), name='transformer_create'),
    path('resource-group/<int:resource_group_id>/attribute/<int:attribute_id>/edit/', views.TransformerEditView.as_view(), name='transformer_edit'),
    path('resource-group/<int:resource_group_id>/attribute/<int:attribute_id>/delete/', views.TransformerDeleteView.as_view(), name='transformer_delete'),
    # Transformer AJAX
    path('resource-group/load-resource-group-attribute/', views.ajax_load_attribute, name='ajax_load_attribute'),

    # Resource CRUD
    path('resource-group/<int:resource_group_id>/resource/', views.ResourceListView.as_view(), name='resource_list'),
    path('resource-group/<int:resource_group_id>/resource/create/', views.ResourceCreateView.as_view(), name='resource_create'),
    path('resource-group/<int:resource_group_id>/resource/<int:pk>/edit/', views.ResourceEditView.as_view(), name='resource_edit'),
    path('resource-group/<int:resource_group_id>/resource/<int:pk>/delete/', views.ResourceDeleteView.as_view(), name='resource_delete'),
    # Resource particular urls
    path('resource-group/<int:resource_group_id>/resource/<int:pk>/move/', views.ResourceMoveView.as_view(), name='resource_move'),
    path('resource-group/<int:resource_group_id>/resource/delete/', views.resource_group_resource_bulk_delete, name='resource_bulk_delete')
]
