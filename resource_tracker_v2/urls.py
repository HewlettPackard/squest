from django.urls import path

from resource_tracker_v2 import views

app_name = 'resource_tracker'

urlpatterns = [
    # attributes
    path('attributes/', views.AttributeListView.as_view(), name='attribute_definition_list'),
    path('attributes/create/', views.attribute_definition_create, name='attribute_definition_create'),
    path('attributes/<int:attribute_definition_id>/edit/', views.attribute_definition_edit,
         name='attribute_definition_edit'),
    path('attributes/<int:attribute_definition_id>/delete/', views.attribute_definition_delete,
         name='attribute_definition_delete'),

    # resource group
    path('resource_group/', views.ResourceGroupListView.as_view(), name='resource_group_list'),
    path('resource_group/create/', views.resource_group_create, name='resource_group_create'),
    path('resource_group/<int:resource_group_id>/edit/', views.resource_group_edit,
         name='resource_group_edit'),
    path('resource_group/<int:resource_group_id>/delete/', views.resource_group_delete,
         name='resource_group_delete'),

    # resource group attributes
    path('resource_group/<int:resource_group_id>/attributes/', views.ResourceGroupAttributeListView.as_view(),
         name='resource_group_attribute_list'),
    path('resource_group/<int:resource_group_id>/attributes/create/',
         views.resource_group_attribute_create,
         name='resource_group_attribute_create'),
    path('resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/edit/',
         views.resource_group_attribute_edit,
         name='resource_group_attribute_edit'),
    path('resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/delete/',
         views.resource_group_attribute_delete,
         name='resource_group_attribute_delete'),
    path('tool/resource_group/load-resource-group-attribute/', views.ajax_load_attribute,
             name='ajax_load_attribute'),
]
