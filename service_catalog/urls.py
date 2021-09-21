from django.conf.urls.static import static
from django.urls import path

from Squest import settings
from . import views
from .views.announcement_list_view import AnnouncementListView
from .views.doc_list_view import DocListView
from .views.global_hook_list_view import GlobalHookListView
from .views.instance_list_view import InstanceListView
from .views.job_template_list_view import JobTemplateListView
from .views.operation_list_view import OperationListView
from .views.request_list_view import RequestListView
from .views.service_list_view import ServiceListView
from .views.support_list_view import SupportListView
from .views.tower_server_list_view import TowerServerListView

app_name = 'service_catalog'


urlpatterns = [
    path('', views.dashboards, name='home'),

    path('dashboards/', views.dashboards, name='dashboards'),

    path('tasks/<int:task_id>/', views.get_task_result, name='get_task_result'),

    path('request/', RequestListView.as_view(), name='request_list'),
    path('request/<int:request_id>/', views.admin_request_details, name='admin_request_details'),
    path('request/<int:request_id>/cancel/', views.customer_request_cancel, name='customer_request_cancel'),
    path('request/<int:request_id>/comment/', views.customer_request_comment, name='customer_request_comment'),
    path('request/<int:request_id>/comment/', views.admin_request_comment, name='admin_request_comment'),
    path('request/<int:request_id>/cancel/', views.admin_request_cancel, name='admin_request_cancel'),
    path('request/<int:request_id>/need-info/', views.admin_request_need_info, name='admin_request_need_info'),
    path('request/<int:request_id>/re-submit/', views.admin_request_re_submit, name='admin_request_re_submit'),
    path('request/<int:request_id>/reject/', views.admin_request_reject, name='admin_request_reject'),
    path('request/<int:request_id>/accept/', views.admin_request_accept, name='admin_request_accept'),
    path('request/<int:request_id>/process/', views.admin_request_process, name='admin_request_process'),

    path('service/', views.service_list, name='service_list'),
    path('service/manage/', ServiceListView.as_view(), name='manage_services'),
    path('service/<int:service_id>/request/', views.customer_service_request, name='customer_service_request'),
    path('service/add_service/', views.add_service, name='create_service'),
    path('service/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('service/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    path('service/<int:service_id>/operation/', OperationListView.as_view(), name='service_operations'),
    path('service/<int:service_id>/operation/add/', views.add_service_operation, name='add_service_operation'),
    path('service/<int:service_id>/operation/<int:operation_id>/delete/',
         views.delete_service_operation, name='delete_service_operation'),
    path('service/<int:service_id>/operation/<int:operation_id>/edit/',
         views.edit_service_operation, name='edit_service_operation'),
    path('service/<int:service_id>/operation/<int:operation_id>/survey/',
         views.service_operation_edit_survey, name='service_operation_edit_survey'),

    path('instance/', InstanceListView.as_view(), name='instance_list'),
    path('instance/<int:instance_id>/', views.instance_details, name='instance_details'),
    path('instance/<int:instance_id>/new-support/', views.instance_new_support,
         name='instance_new_support'),
    path('instance/<int:instance_id>/support/<int:support_id>/', views.instance_support_details,
         name='instance_support_details'),
    path('instance/<int:instance_id>/edit/', views.instance_edit, name='instance_edit'),
    path('instance/<int:instance_id>/archive/', views.instance_archive, name='instance_archive'),
    path('instance/<int:instance_id>/operation/<int:operation_id>/', views.instance_request_new_operation,
         name='instance_request_new_operation'),

    path('support/', SupportListView.as_view(), name='support_list'),

    path('doc/', DocListView.as_view(), name='doc_list'),
    path('doc/<int:doc_id>/show/', views.doc_show, name='doc_show'),

    path('tower/', TowerServerListView.as_view(), name='list_tower'),
    path('tower/add/', views.add_tower, name='add_tower'),
    path('tower/<int:tower_id>/sync/', views.sync_tower, name='sync_tower'),
    path('tower/<int:tower_id>/sync/<int:job_template_id>', views.sync_tower, name='sync_job_template'),
    path('tower/<int:tower_id>/delete/', views.delete_tower, name='delete_tower'),
    path('tower/<int:tower_id>/update/', views.update_tower, name='update_tower'),
    path('tower/<int:tower_id>/job_template/', JobTemplateListView.as_view(), name='tower_job_templates_list'),
    path('tower/<int:tower_id>/job_template/<int:job_template_id>/delete/', views.delete_job_template,
         name='delete_job_template'),
    path('tower/<int:tower_id>/job_template/<int:job_template_id>/compliancy/', views.job_template_compliancy,
         name='job_template_compliancy'),
    path('tower/<int:tower_id>/job_template/<int:job_template_id>/', views.job_template_details,
         name='job_template_details'),

    path('tool/global_hook/', GlobalHookListView.as_view(), name='global_hook_list'),
    path('tool/global_hook/create/', views.global_hook_create, name='global_hook_create'),
    path('tool/global_hook/<int:global_hook_id>/edit/', views.global_hook_edit, name='global_hook_edit'),
    path('tool/global_hook/<int:global_hook_id>/delete/', views.global_hook_delete, name='global_hook_delete'),
    path('tool/global_hook/create/ajax/load-model-state/', views.ajax_load_model_state,
         name='ajax_load_model_state'),

    path('tool/announcement/', AnnouncementListView.as_view(), name='announcement_list'),
    path('tool/announcement/create/', views.announcement_create, name='announcement_create'),
    path('tool/announcement/<int:announcement_id>/edit/', views.announcement_edit, name='announcement_edit'),
    path('tool/announcement/<int:announcement_id>/delete/', views.announcement_delete, name='announcement_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
