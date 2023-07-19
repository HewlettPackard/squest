from django.urls import path

from . import views

app_name = 'service_catalog'
urlpatterns = [
    path('', views.service_catalog_list, name='service_catalog_list'),

    # Request CRUD
    path('request/', views.RequestListView.as_view(), name='request_list'),
    path('request/<int:pk>/', views.RequestDetailView.as_view(), name='request_details'),
    path('request/<int:pk>/edit/', views.RequestEditView.as_view(), name='request_edit'),
    path('request/<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request_delete'),

    # Request State Machine
    path('request/<int:request_id>/cancel/', views.request_cancel, name='request_cancel'),
    path('request/<int:request_id>/need-info/', views.request_need_info, name='request_need_info'),
    path('request/<int:request_id>/re-submit/', views.request_re_submit, name='request_re_submit'),
    path('request/<int:request_id>/reject/', views.request_reject, name='request_reject'),
    path('request/<int:request_id>/accept/', views.request_accept, name='request_accept'),
    path('request/<int:request_id>/process/', views.request_process, name='request_process'),
    path('request/<int:request_id>/archive/', views.request_archive, name='request_archive'),
    path('request/<int:request_id>/unarchive/', views.request_unarchive, name='request_unarchive'),

    # Request bulk delete
    path('request/delete-confirm/', views.request_bulk_delete_confirm, name='request_bulk_delete_confirm'),
    path('request/delete-force/', views.request_bulk_delete, name='request_bulk_delete'),

    # Archived request list
    path('request/archived/', views.RequestArchivedListView.as_view(), name='request_archived_list'),

    # Request comments CRUD
    path('request/<int:request_id>/comment/<int:comment_id>/', views.requestmessage_edit,
         name='requestmessage_edit'),
    path('request/<int:request_id>/comment/', views.request_comment, name='requestmessage_create'),

    # Portfolio CRUD
    path('portfolio/', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolio/create/', views.PortfolioCreateView.as_view(), name='portfolio_create'),
    path('portfolio/<int:pk>/edit/', views.PortfolioEditView.as_view(), name='portfolio_edit'),
    path('portfolio/<int:pk>/delete/', views.PortfolioDeleteView.as_view(), name='portfolio_delete'),

    # Service CRUD
    path('service/', views.ServiceListView.as_view(), name='service_list'),
    path('service/create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('service/<int:pk>/edit/', views.ServiceEditView.as_view(), name='service_edit'),
    path('service/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),

    # Operation CRUD
    path('service/<int:service_id>/operation/', views.OperationListView.as_view(), name='operation_list'),
    path('service/<int:service_id>/operation/create/', views.OperationCreateView.as_view(), name='operation_create'),
    path('service/<int:service_id>/operation/<int:pk>/delete/', views.OperationDeleteView.as_view(), name='operation_delete'),
    path('service/<int:service_id>/operation/<int:pk>/edit/', views.OperationEditView.as_view(), name='operation_edit'),

    # Request operation endpoints
    path('service/<int:service_id>/operation/<int:operation_id>/request/', views.request_service,
         name='request_service'),
    path('service/<int:service_id>/operation/request/', views.CreateOperationListView.as_view(),
         name='create_operation_list'),

    # Edit operation survey endpoint
    path('service/<int:service_id>/operation/<int:pk>/survey/', views.operation_edit_survey, name='operation_edit_survey'),

    # Instance CRUD
    path('instance/', views.InstanceListView.as_view(), name='instance_list'),
    path('instance/<int:pk>/edit/', views.InstanceEditView.as_view(), name='instance_edit'),
    path('instance/<int:pk>/delete/', views.InstanceDeleteView.as_view(), name='instance_delete'),
    path('instance/<int:pk>/', views.InstanceDetailView.as_view(), name='instance_details'),

    # Instance bulk delete
    path('instance/delete-confirm/', views.instance_bulk_delete_confirm, name='instance_bulk_delete_confirm'),
    path('instance/delete-force/', views.instance_bulk_delete, name='instance_bulk_delete'),

    # Instance message
    path('instance/<int:instance_id>/support/<int:support_id>/message/<int:message_id>/', views.support_message_edit,
         name='support_message_edit'),
    # Instance State Machine
    path('instance/<int:instance_id>/archive/', views.instance_archive, name='instance_archive'),

    # Instance request operation
    path('instance/<int:instance_id>/operation/<int:operation_id>/', views.instance_request_new_operation,
         name='instance_request_new_operation'),

    # Support CRUD
    path('support/', views.SupportListView.as_view(), name='support_list'),
    # Support CRUD under instance
    path('instance/<int:pk>/support/create/', views.instance_new_support,
         name='instance_new_support'),
    path('instance/<int:instance_id>/support/<int:support_id>/', views.instance_support_details,
         name='instance_support_details'),

    # Support State Machine
    path('instance/<int:instance_id>/support/<int:support_id>/close/', views.CloseSupportView.as_view(),
         name='instance_support_close'),
    path('instance/<int:instance_id>/support/<int:support_id>/reopen/', views.ReOpenSupportView.as_view(),
         name='instance_support_reopen'),

    # Doc CRUD
    path('doc/', views.DocListView.as_view(), name='doc_list'),
    path('doc/<int:doc_id>/', views.doc_show, name='doc_show'),

    # Controller CRUD
    path('controller/', views.TowerServerListView.as_view(), name='towerserver_list'),
    path('controller/create/', views.TowerServerCreateView.as_view(), name='towerserver_create'),
    path('controller/<int:pk>/edit/', views.TowerServerEditView.as_view(), name='towerserver_edit'),
    path('controller/<int:pk>/delete/', views.TowerServerDeleteView.as_view(), name='towerserver_delete'),

    # Synchronize controller endpoints
    path('controller/<int:tower_id>/sync/', views.towerserver_sync, name='towerserver_sync'),
    path('controller/<int:tower_id>/sync/<int:pk>', views.towerserver_sync, name='sync_job_template'),

    # Job Template CRUD
    path('controller/<int:tower_id>/job_template/', views.JobTemplateListView.as_view(),
         name='jobtemplate_list'),
    path('tower/<int:tower_id>/job_template/<int:pk>/', views.JobTemplateDetailView.as_view(),
         name='jobtemplate_details'),
    path('controller/<int:tower_id>/job_template/<int:pk>/delete/', views.JobTemplateDeleteView.as_view(),
         name='jobtemplate_delete'),

    # Job Template compliance details
    path('tower/<int:tower_id>/job_template/<int:pk>/compliancy/', views.job_template_compliancy,
         name='job_template_compliancy'),

    # Global Hook CRUD
    path('tool/global_hook/', views.GlobalHookListView.as_view(), name='globalhook_list'),
    path('tool/global_hook/create/', views.GlobalHookCreateView.as_view(), name='globalhook_create'),
    path('tool/global_hook/<int:pk>/edit/', views.GlobalHookEditView.as_view(), name='globalhook_edit'),
    path('tool/global_hook/<int:pk>/delete/', views.GlobalHookDeleteView.as_view(), name='globalhook_delete'),

    # Global Hook AJAX
    path('tool/global_hook/create/ajax/load-model-state/', views.ajax_load_model_state,
         name='ajax_load_model_state'),
    path('tool/global_hook/create/ajax/load-service-operations/', views.ajax_load_service_operations,
         name='ajax_load_service_operations'),

    # Announcement CRUD
    path('tool/announcement/', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('tool/announcement/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('tool/announcement/<int:pk>/edit/', views.AnnouncementEditView.as_view(), name='announcement_edit'),
    path('tool/announcement/<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='announcement_delete'),

    # Custom Link CRUD
    path('tool/custom-link/', views.CustomLinkListView.as_view(), name='customlink_list'),
    path('tool/custom-link/create/', views.CustomLinkCreateView.as_view(), name='customlink_create'),
    path('tool/custom-link/<int:pk>/edit/', views.CustomLinkEditView.as_view(), name='customlink_edit'),
    path('tool/custom-link/<int:pk>/delete/', views.CustomLinkDeleteView.as_view(), name='customlink_delete'),

]
