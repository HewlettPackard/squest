from django.urls import path

from resource_tracker import views

urlpatterns = [

    path('resource_group/', views.resource_group_list, name='resource_group_list'),
    path('resource_group/create/', views.resource_group_create, name='resource_group_create'),
    path('resource_group/<int:resource_group_id>/edit/', views.resource_group_edit,
         name='resource_group_edit'),
    path('resource_group/<int:resource_group_id>/delete/', views.resource_group_delete,
         name='resource_group_delete'),
    path('resource_group/<int:resource_group_id>/attributes/', views.resource_group_attribute_list,
         name='resource_group_attribute_list'),
    path('resource_group/<int:resource_group_id>/attributes/create/',
         views.resource_group_attribute_create,
         name='resource_group_attribute_create'),
    path('resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/',
         views.resource_group_attribute_edit,
         name='resource_group_attribute_edit'),
    path('resource_group/<int:resource_group_id>/attributes/<int:attribute_id>/delete/',
         views.resource_group_attribute_delete,
         name='resource_group_attribute_delete'),
    path('resource_group/<int:resource_group_id>/resources/',
         views.resource_group_resource_list,
         name='resource_group_resource_list'),
    path('resource_group/<int:resource_group_id>/resources/create/',
         views.resource_group_resource_create,
         name='resource_group_resource_create'),
    path('resource_group/<int:resource_group_id>/resources/<int:resource_id>/delete/',
         views.resource_group_resource_delete,
         name='resource_group_resource_delete'),
    path('resource_group/<int:resource_group_id>/resources/<int:resource_id>/edit/',
         views.resource_group_resource_edit,
         name='resource_group_resource_edit'),
]