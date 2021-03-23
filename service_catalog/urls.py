from django.urls import path
from django.conf.urls.static import static

from TowerServiceCatalog import settings
from . import views

urlpatterns = [
    # common URLs
    path('', views.home, name='home'),
    path('tasks/<int:task_id>/', views.get_task_result, name='get_task_result'),

    # settings URLs
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
    path('settings/catalog/service/<int:service_id>/operations/<int:operation_id>/survey/',
         views.service_operation_edit_survey,
         name='service_operation_edit_survey'),

    # customer views URLs
    path('customer/catalog/service/', views.customer_list_service, name='customer_service_list'),
    path('customer/catalog/service/<int:service_id>/request/', views.customer_service_request,
         name='customer_service_request'),
    path('customer/request/', views.customer_request_list, name='customer_request_list'),
    path('customer/request/<int:request_id>/cancel/', views.customer_request_cancel, name='customer_request_cancel'),

    path('customer/instance/', views.customer_instance_list, name='customer_instance_list'),
    path('customer/instance/<int:instance_id>/', views.customer_instance_details, name='customer_instance_details'),
    # path('customer/instance/<int:instance_id>/operations/', views.customer_instance_operation_list,
    #      name='customer_instance_operation_list'),

    # admin views URLs
    path('admin/request/', views.admin_request_list, name='admin_request_list'),
    path('admin/request/<int:request_id>/cancel/', views.admin_request_cancel, name='admin_request_cancel'),
    path('admin/request/<int:request_id>/need-info/', views.admin_request_need_info, name='admin_request_need_info'),
    path('admin/request/<int:request_id>/re-submit/', views.admin_request_re_submit, name='admin_request_re_submit'),
    path('admin/request/<int:request_id>/reject/', views.admin_request_reject, name='admin_request_reject'),
    path('admin/request/<int:request_id>/accept/', views.admin_request_accept, name='admin_request_accept'),
    path('admin/request/<int:request_id>/process/', views.admin_request_process, name='admin_request_process'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
