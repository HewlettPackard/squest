from django.urls import path

from resource_tracker_v2 import views

app_name = 'resource_tracker_v2'

urlpatterns = [
    # Attribute definition CRUD
    path('attributes/', views.AttributeDefinitionListView.as_view(), name='attributedefinition_list'),
    path('attributes/create/', views.AttributeDefinitionCreateView.as_view(), name='attributedefinition_create'),
    path('attributes/<int:pk>/', views.AttributeDefinitionDetailView.as_view(), name='attributedefinition_details'),
    path('attributes/<int:pk>/edit/', views.AttributeDefinitionEditView.as_view(), name='attributedefinition_edit'),
    path('attributes/<int:pk>/delete/', views.AttributeDefinitionDeleteView.as_view(), name='attributedefinition_delete'),

    # Resource group CRUD
    path('resource_group/', views.ResourceGroupListView.as_view(), name='resourcegroup_list'),
    path('resource_group/table/', views.ResourceGroupListViewCSV.as_view(), name='resourcegroup_list_table'),
    path('resource_group/create/', views.ResourceGroupCreateView.as_view(), name='resourcegroup_create'),
    path('resource_group/<int:pk>/', views.ResourceGroupDetailView.as_view(), name='resourcegroup_details'),
    path('resource_group/<int:pk>/edit/', views.ResourceGroupEditView.as_view(), name='resourcegroup_edit'),
    path('resource_group/<int:pk>/delete/', views.ResourceGroupDeleteView.as_view(), name='resourcegroup_delete'),
    # Graph
    path('resource_tracker_graph/', views.resource_tracker_graph, name='resource_tracker_graph'),

    # Transformer CRUD
    path('resource_group/<int:resource_group_id>/attributes/', views.TransformerListView.as_view(), name='transformer_list'),
    path('resource_group/<int:resource_group_id>/attributes/create/', views.TransformerCreateView.as_view(), name='transformer_create'),
    path('resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/edit/', views.TransformerEditView.as_view(), name='transformer_edit'),
    path('resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/delete/', views.TransformerDeleteView.as_view(), name='transformer_delete'),
    # Transformer AJAX
    path('resource_group/load-resource-group-attribute/', views.ajax_load_attribute, name='ajax_load_attribute'),

    # Resource CRUD
    path('resource_group/<int:resource_group_id>/resources/', views.ResourceListView.as_view(), name='resource_list'),
    path('resource_group/<int:resource_group_id>/resources/create/', views.ResourceCreateView.as_view(), name='resource_create'),
    path('resource_group/<int:resource_group_id>/resources/<int:pk>/edit/', views.ResourceEditView.as_view(), name='resource_edit'),
    path('resource_group/<int:resource_group_id>/resources/<int:pk>/delete/', views.ResourceDeleteView.as_view(), name='resource_delete'),
    # Resource particular urls
    path('resource_group/<int:resource_group_id>/resources/<int:pk>/move/', views.ResourceMoveView.as_view(), name='resource_move'),
    path('resource_group/<int:resource_group_id>/resources/delete/', views.resource_group_resource_bulk_delete, name='resource_bulk_delete')
]
