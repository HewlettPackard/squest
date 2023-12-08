from django.urls import path

from . import views
from .forms import ServiceInstanceForm, ServiceRequestForm

app_name = 'service_catalog'
urlpatterns = [
    path('', views.service_catalog_list, name='service_catalog_list'),

    # Request CRUD
    path('request/', views.RequestListView.as_view(), name='request_list'),
    path('request/<int:pk>/', views.RequestDetailView.as_view(), name='request_details'),
    path('request/<int:pk>/edit/', views.RequestEditView.as_view(), name='request_edit'),
    path('request/<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request_delete'),

    # Request State Machine
    path('request/<int:pk>/cancel/', views.request_cancel, name='request_cancel'),
    path('request/<int:pk>/need-info/', views.request_need_info, name='request_need_info'),
    path('request/<int:pk>/re-submit/', views.RequestReSubmitView.as_view(), name='request_re_submit'),
    path('request/<int:pk>/reject/', views.request_reject, name='request_reject'),
    path('request/<int:pk>/accept/', views.request_accept, name='request_accept'),
    path('request/<int:pk>/process/', views.request_process, name='request_process'),
    path('request/<int:pk>/archive/', views.request_archive, name='request_archive'),
    path('request/<int:pk>/unarchive/', views.request_unarchive, name='request_unarchive'),
    path('request/<int:pk>/approve/', views.RequestApproveView.as_view(), name='request_approve'),


    # Request bulk delete
    path('request/delete/', views.request_bulk_delete, name='request_bulk_delete'),

    # Archived request list
    path('request/archived/', views.RequestArchivedListView.as_view(), name='request_archived_list'),

    # Request message CRUD
    path('request/<int:request_id>/comment/<int:pk>/', views.requestmessage_edit,
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
    path('service/<int:pk>/', views.ServiceDetailView.as_view(), name='service_details'),

    # Operation CRUD
    path('operation/', views.OperationListView.as_view(), name='operation_list'),
    path('operation/create/', views.OperationCreateView.as_view(), name='operation_create'),
    path('operation/<int:pk>/delete/', views.OperationDeleteView.as_view(), name='operation_delete'),
    path('operation/<int:pk>/edit/', views.OperationEditView.as_view(), name='operation_edit'),
    path('operation/<int:pk>/', views.OperationDetailView.as_view(), name='operation_details'),

    # Request operation endpoints
    path('service/<int:service_id>/operation/<int:operation_id>/request/',
         views.ServiceRequestWizardView.as_view([ServiceInstanceForm, ServiceRequestForm]), name='request_service'),

    path('service/<int:service_id>/operation/request/', views.CreateOperationListView.as_view(),
         name='create_operation_list'),

    # Edit operation survey endpoint
    path('operation/<int:pk>/survey/', views.operation_edit_survey, name='operation_edit_survey'),

    # Instance CRUD
    path('instance/', views.InstanceListView.as_view(), name='instance_list'),
    path('instance/<int:pk>/edit/', views.InstanceEditView.as_view(), name='instance_edit'),
    path('instance/<int:pk>/delete/', views.InstanceDeleteView.as_view(), name='instance_delete'),
    path('instance/<int:pk>/', views.InstanceDetailView.as_view(), name='instance_details'),

    # Instance bulk delete
    path('instance/delete/', views.instance_bulk_delete, name='instance_bulk_delete'),

    # Archived instance list
    path('instance/archived/', views.InstanceArchivedListView.as_view(), name='instance_archived_list'),

    # Instance State Machine
    path('instance/<int:pk>/archive/', views.instance_archive, name='instance_archive'),
    path('instance/<int:pk>/unarchive/', views.instance_unarchive, name='instance_unarchive'),

    # Instance request operation
    path('instance/<int:instance_id>/operation/<int:operation_id>/', views.instance_request_new_operation,
         name='instance_request_new_operation'),

    # Support CRUD
    path('support/', views.SupportListView.as_view(), name='support_list'),
    # Support CRUD under instance
    path('instance/<int:instance_id>/support/create/', views.support_create, name='support_create'),
    path('instance/<int:instance_id>/support/<int:pk>/', views.support_details, name='support_details'),
    path('instance/<int:instance_id>/support/<int:pk>/delete/', views.SupportDeleteView.as_view(), name='support_delete'),

    # Support State Machine
    path('instance/<int:instance_id>/support/<int:pk>/close/', views.CloseSupportView.as_view(), name='support_close'),
    path('instance/<int:instance_id>/support/<int:pk>/reopen/', views.ReOpenSupportView.as_view(), name='support_reopen'),

    # Support message
    path('instance/<int:instance_id>/support/<int:support_id>/message/<int:pk>/', views.supportmessage_edit,
         name='supportmessage_edit'),

    # Doc CRUD
    path('doc/', views.DocListView.as_view(), name='doc_list'),
    path('doc/<int:pk>/', views.doc_details, name='doc_details'),

    # Tower server CRUD
    path('tower/', views.TowerServerListView.as_view(), name='towerserver_list'),
    path('tower/create/', views.TowerServerCreateView.as_view(), name='towerserver_create'),
    path('tower/<int:pk>/', views.TowerServerDetailView.as_view(), name='towerserver_details'),
    path('tower/<int:pk>/edit/', views.TowerServerEditView.as_view(), name='towerserver_edit'),
    path('tower/<int:pk>/delete/', views.TowerServerDeleteView.as_view(), name='towerserver_delete'),

    # Synchronize tower server endpoints
    path('tower/<int:tower_id>/sync/', views.towerserver_sync, name='towerserver_sync'),
    path('tower/<int:tower_id>/sync/<int:pk>', views.towerserver_sync, name='jobtemplate_sync'),

    # Job Template CRUD
    path('tower/<int:tower_id>/job-template/', views.JobTemplateListView.as_view(),
         name='jobtemplate_list'),
    path('tower/<int:tower_id>/job-template/<int:pk>/', views.JobTemplateDetailView.as_view(),
         name='jobtemplate_details'),
    path('tower/<int:tower_id>/job-template/<int:pk>/delete/', views.JobTemplateDeleteView.as_view(),
         name='jobtemplate_delete'),

    # Job Template compliance details
    path('tower/<int:tower_id>/job-template/<int:pk>/compliancy/', views.job_template_compliancy,
         name='job_template_compliancy'),

    # Global Hook Instance CRUD
    path('tool/global-hook-instance/', views.InstanceHookListView.as_view(), name='instancehook_list'),
    path('tool/global-hook-instance/create/', views.InstanceHookCreateView.as_view(),
         name='instancehook_create'),
    path('tool/global-hook-instance/<int:pk>/edit/', views.InstanceHookEditView.as_view(),
         name='instancehook_edit'),
    path('tool/global-hook-instance/<int:pk>/delete/', views.InstanceHookDeleteView.as_view(),
         name='instancehook_delete'),

    # Global Hook Request CRUD
    path('tool/global-hook-request/', views.RequestHookListView.as_view(), name='requesthook_list'),
    path('tool/global-hook-request/create/', views.RequestHookCreateView.as_view(),
         name='requesthook_create'),
    path('tool/global-hook-request/<int:pk>/edit/', views.RequestHookEditView.as_view(),
         name='requesthook_edit'),
    path('tool/global-hook-request/<int:pk>/delete/', views.RequestHookDeleteView.as_view(),
         name='requesthook_delete'),

    # Announcement CRUD
    path('administration/announcement/', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('administration/announcement/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('administration/announcement/<int:pk>/edit/', views.AnnouncementEditView.as_view(), name='announcement_edit'),
    path('administration/announcement/<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='announcement_delete'),

    # Custom Link CRUD
    path('administration/custom-link/', views.CustomLinkListView.as_view(), name='customlink_list'),
    path('administration/custom-link/create/', views.CustomLinkCreateView.as_view(), name='customlink_create'),
    path('administration/custom-link/<int:pk>/edit/', views.CustomLinkEditView.as_view(), name='customlink_edit'),
    path('administration/custom-link/<int:pk>/delete/', views.CustomLinkDeleteView.as_view(), name='customlink_delete'),

    # Approval Workflow CRUD
    path('administration/approval/', views.ApprovalWorkflowListView.as_view(), name='approvalworkflow_list'),
    path('administration/approval/<int:pk>/', views.ApprovalWorkflowDetailView.as_view(), name='approvalworkflow_details'),
    path('administration/approval/create/', views.ApprovalWorkflowCreateView.as_view(), name='approvalworkflow_create'),
    path('administration/approval/<int:pk>/edit/', views.ApprovalWorkflowEditView.as_view(), name='approvalworkflow_edit'),
    path('administration/approval/<int:pk>/delete/', views.ApprovalWorkflowDeleteView.as_view(), name='approvalworkflow_delete'),
    path('administration/approval/<int:pk>/reset_requests/', views.ApprovalWorkflowResetRequests.as_view(), name='approvalworkflow_reset_requests'),
    # Approval Workflow ajax
    path('administration/approval/step_position_update/',
         views.ajax_approval_step_position_update, name='ajax_approval_step_position_update'),

    # Approval Step CRUD
    path('administration/approval/<int:approval_workflow_id>/approval-step/create/', views.ApprovalStepCreateView.as_view(),
         name='approvalstep_create'),
    path('administration/approval/<int:approval_workflow_id>/approval-step/<int:pk>/edit/',
         views.ApprovalStepEditView.as_view(),
         name='approvalstep_edit'),
    path('administration/approval/<int:approval_workflow_id>/approval-step/<int:pk>/delete/',
         views.ApprovalStepDeleteView.as_view(),
         name='approvalstep_delete'),

    # Email template
    path('administration/email-template/', views.EmailTemplateListView.as_view(), name='emailtemplate_list'),
    path('administration/email-template/<int:pk>/', views.EmailTemplateDetailView.as_view(), name='emailtemplate_details'),
    path('administration/email-template/create/', views.EmailTemplateCreateView.as_view(), name='emailtemplate_create'),
    path('administration/email-template/<int:pk>/edit/', views.EmailTemplateEditView.as_view(), name='emailtemplate_edit'),
    path('administration/email-template/<int:pk>/delete/', views.EmailTemplateDeleteView.as_view(), name='emailtemplate_delete'),
    path('administration/email-template/<int:pk>/send/', views.EmailTemplateSend.as_view(), name='emailtemplate_send'),

]
