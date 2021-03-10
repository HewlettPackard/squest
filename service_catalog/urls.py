from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/<int:task_id>/', views.get_task_result, name='get_task_result'),
    path('settings/tower/', views.tower, name='tower'),
    path('settings/tower/add/', views.add_tower, name='add_tower'),
    path('settings/tower/<int:tower_id>/sync/', views.sync_tower, name='sync_tower'),
    path('settings/tower/<int:tower_id>/delete/', views.delete_tower, name='delete_tower'),
    path('settings/tower/<int:tower_id>/update/', views.update_tower, name='update_tower'),
    path('settings/tower/<int:tower_id>/job_templates/', views.tower_job_templates, name='tower_job_templates'),
    path('settings/tower/<int:tower_id>/job_templates/<int:job_template_id>/delete', views.delete_job_template,
         name='delete_job_template'),

    path('settings/catalog/service/', views.service, name='settings_catalog'),
    path('settings/catalog/service/add_service/', views.add_service, name='settings_catalog_add_service'),
    path('settings/catalog/service/<int:service_id>/operations/', views.service_operations, name='service_operations'),
    path('settings/catalog/service/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('settings/catalog/service/<int:service_id>/operations/add/', views.add_service_operation,
         name='add_service_operation'),
    path('settings/catalog/service/<int:service_id>/operations/<int:operation_id>/delete/',
         views.delete_service_operation,
         name='delete_service_operation'),
]
