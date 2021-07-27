from django.conf.urls.static import static
from django.urls import path

from Squest import settings
from . import views

app_name = 'service_catalog'

urlpatterns = [
    # common URLs
    path('', views.home, name='home'),
    path('tasks/<int:task_id>/', views.get_task_result, name='get_task_result'),

    # settings URLs
    path('settings/tower/', views.list_tower, name='list_tower'),
    path('settings/tower/add/', views.add_tower, name='add_tower'),
    path('settings/tower/<int:tower_id>/sync/', views.sync_tower, name='sync_tower'),
    path('settings/tower/<int:tower_id>/delete/', views.delete_tower, name='delete_tower'),
    path('settings/tower/<int:tower_id>/update/', views.update_tower, name='update_tower'),
    path('settings/tower/<int:tower_id>/job_templates/', views.tower_job_templates_list,
         name='tower_job_templates_list'),
    path('settings/tower/<int:tower_id>/job_templates/<int:job_template_id>/delete', views.delete_job_template,
         name='delete_job_template'),

    path('settings/catalog/service/', views.service, name='service_list'),
    path('settings/catalog/service/add_service/', views.add_service, name='create_service'),
    path('settings/catalog/service/<int:service_id>/operations/', views.service_operations, name='service_operations'),
    path('settings/catalog/service/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('settings/catalog/service/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    path('settings/catalog/service/<int:service_id>/operations/add/', views.add_service_operation,
         name='add_service_operation'),
    path('settings/catalog/service/<int:service_id>/operations/<int:operation_id>/delete/',
    views.delete_service_operation, name='delete_service_operation'),
    path('settings/catalog/service/<int:service_id>/operations/<int:operation_id>/edit/',
    views.edit_service_operation, name='edit_service_operation'),
    path('settings/catalog/service/<int:service_id>/operations/<int:operation_id>/survey/',
    views.service_operation_edit_survey, name='service_operation_edit_survey'),
    path('settings/global_hook/', views.global_hook_list, name='global_hook_list'),
    path('settings/global_hook/create/', views.global_hook_create, name='global_hook_create'),
    path('settings/global_hook/<int:global_hook_id>/edit/', views.global_hook_edit, name='global_hook_edit'),
    path('settings/global_hook/<int:global_hook_id>/delete/', views.global_hook_delete, name='global_hook_delete'),
    path('settings/global_hook/create/ajax/load-model-state/', views.ajax_load_model_state,
         name='ajax_load_model_state'),

    # customer views URLs
    path('customer/catalog/service/', views.customer_list_service, name='customer_service_list'),
    path('customer/catalog/service/<int:service_id>/request/', views.customer_service_request,
         name='customer_service_request'),
    path('customer/request/', views.customer_request_list, name='customer_request_list'),
    path('customer/request/<int:request_id>/cancel/', views.customer_request_cancel, name='customer_request_cancel'),
    path('customer/request/<int:request_id>/comment/', views.customer_request_comment, name='customer_request_comment'),

    path('customer/instance/', views.customer_instance_list, name='customer_instance_list'),
    path('customer/instance/<int:instance_id>/', views.customer_instance_details, name='customer_instance_details'),
    path('customer/instance/<int:instance_id>/new-support/', views.customer_instance_new_support,
         name='customer_instance_new_support'),
    path('customer/instance/<int:instance_id>/support/<int:support_id>', views.customer_instance_support_details,
         name='customer_instance_support_details'),
    path('customer/instance/<int:instance_id>/archive/', views.customer_instance_archive,
         name='customer_instance_archive'),
    path('customer/instance/<int:instance_id>/operation/<int:operation_id>/',
    views.customer_instance_request_new_operation, name='customer_instance_request_new_operation'),

    # admin views URLs
    path('admin/request/', views.admin_request_list, name='admin_request_list'),
    path('admin/request/<int:request_id>/comment/', views.admin_request_comment, name='admin_request_comment'),
    path('admin/request/<int:request_id>/cancel/', views.admin_request_cancel, name='admin_request_cancel'),
    path('admin/request/<int:request_id>/need-info/', views.admin_request_need_info, name='admin_request_need_info'),
    path('admin/request/<int:request_id>/re-submit/', views.admin_request_re_submit, name='admin_request_re_submit'),
    path('admin/request/<int:request_id>/reject/', views.admin_request_reject, name='admin_request_reject'),
    path('admin/request/<int:request_id>/accept/', views.admin_request_accept, name='admin_request_accept'),
    path('admin/request/<int:request_id>/process/', views.admin_request_process, name='admin_request_process'),

    path('admin/instance/', views.admin_instance_list, name='admin_instance_list'),
    path('admin/instance/<int:instance_id>/', views.admin_instance_details, name='admin_instance_details'),
    path('admin/instance/<int:instance_id>/new-support/', views.admin_instance_new_support,
         name='admin_instance_new_support'),
    path('admin/instance/<int:instance_id>/support/<int:support_id>', views.admin_instance_support_details,
         name='admin_instance_support_details'),
    path('admin/instance/<int:instance_id>/edit/', views.admin_instance_edit, name='admin_instance_edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
