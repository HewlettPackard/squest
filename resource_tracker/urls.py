from django.urls import path

from resource_tracker import views

urlpatterns = [

    path('resource_group/', views.resource_group_list, name='resource_group_list'),
    path('resource_group/resource_group_create', views.resource_group_create, name='resource_group_create'),
    path('resource_group/resource_group/<int:resource_group_id>/attributes', views.resource_group_attribute_list,
         name='resource_group_attribute_list'),
    path('resource_group/resource_group/<int:resource_group_id>/attributes/create',
         views.resource_group_attribute_create,
         name='resource_group_attribute_create'),
    path('resource_group/resource_group/<int:resource_group_id>/attributes/<int:attribute_id>',
         views.resource_group_attribute_edit,
         name='resource_group_attribute_edit'),
    path('resource_group/resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/delete',
         views.resource_group_attribute_delete,
         name='resource_group_attribute_delete'),
]