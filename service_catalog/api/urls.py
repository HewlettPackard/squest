from django.urls import path

from service_catalog.api.views import *
from service_catalog.api.views.custom_link_api_views import CustomLinkDetails, CustomLinkListCreate

urlpatterns = [
    # Instance CRUD
    path('instance/', InstanceList.as_view(), name='api_instance_list_create'),
    path('instance/<int:pk>/', InstanceDetails.as_view(), name='api_instance_details'),
    # Instance spec
    path('instance/<int:pk>/spec/', SpecDetailsAPIView.as_view(), name='api_instance_spec_details'),
    path('instance/<int:pk>/user-spec/', UserSpecDetailsAPIView.as_view(), name='api_instance_user_spec_details'),
    # Instance request operation
    path('instance/<int:instance_id>/operation/<int:operation_id>/request/', OperationRequestCreate.as_view(),
         name='api_operation_request_create'),

    # Request
    path('request/', RequestList.as_view(), name='api_request_list'),
    path('request/<int:pk>/', RequestDetails.as_view(), name='api_request_details'),
    # Request state machine
    path('request/<int:pk>/accept/', RequestStateMachine.as_view({'post': 'accept', 'get': 'get_survey'}),
         name='api_request_accept'),
    path('request/<int:pk>/archive/', RequestStateMachine.as_view({'post': 'archive'}),
         name='api_request_archive'),
    path('request/<int:pk>/cancel/', RequestStateMachine.as_view({'post': 'cancel'}),
         name='api_request_cancel'),
    path('request/<int:pk>/need-info/', RequestStateMachine.as_view({'post': 'need_info'}),
         name='api_request_need_info'),
    path('request/<int:pk>/process/', RequestStateMachine.as_view({'post': 'process'}),
         name='api_request_process'),
    path('request/<int:pk>/re-submit/', RequestStateMachine.as_view({'post': 're_submit'}),
         name='api_request_re_submit'),
    path('request/<int:pk>/reject/', RequestStateMachine.as_view({'post': 'reject'}),
         name='api_request_reject'),
    path('request/<int:pk>/unarchive/', RequestStateMachine.as_view({'post': 'unarchive'}),
         name='api_request_unarchive'),
    # Approval Workflow state machine
    path('request/<int:pk>/approval_workflow_state/', ApprovalWorkflowStateDetails.as_view(),
         name='api_request_approval_workflow_state'),
    path('request/<int:pk>/approval_workflow_state/approve/',
         ApproveCurrentStep.as_view({'get': 'get_survey', 'post': 'approve'}),
         name='api_request_approval_workflow_state_approve'),
    path('request/<int:pk>/approval_workflow_state/reject/',
         ApproveCurrentStep.as_view({'get': 'get_survey', 'post': 'reject'}),
         name='api_request_approval_workflow_state_reject'),

    # Service CRUD
    path('service/', ServiceListCreate.as_view(), name='api_service_list_create'),
    path('service/<int:pk>/', ServiceDetails.as_view(), name='api_service_details'),
    # Service request
    path('service/<int:service_id>/operation/<int:pk>/request/', ServiceRequestCreate.as_view(),
         name='api_service_request_create'),

    # Operation CRUD
    path('operation/', OperationListCreate.as_view(), name='api_operation_list_create'),
    path('operation/<int:pk>/', OperationDetails.as_view(), name='api_operation_details'),
    # Instance operations list
    path('instance/<int:instance_id>/operation/', InstanceOperationList.as_view(), name='api_instance_operation_list'),
    # Operation survey
    path('peration/<int:pk>/survey/', OperationSurveyAPI.as_view(), name='api_operation_survey_list_update'),

    # TowerServer CRUD
    path('tower/', TowerServerList.as_view(), name='api_towerserver_list_create'),
    path('tower/<int:pk>/', TowerServerDetails.as_view(), name='api_towerserver_details'),
    # JobTemplate sync all
    path('tower/<int:tower_server_id>/job_template/sync/', JobTemplateSync.as_view(),
         name='api_jobtemplate_sync_all'),
    # JobTemplate sync
    path('tower/<int:tower_server_id>/job_template/<int:job_template_id>/sync/', JobTemplateSync.as_view(),
         name='api_jobtemplate_sync'),

    # JobTemplate CRUD
    path('job_template/', JobTemplateList.as_view(), name='api_jobtemplate_list'),
    path('job_template/<int:pk>/', JobTemplateDetails.as_view(), name='api_jobtemplate_details'),

    # Portfolio CRUD
    path('portfolio/', PortfolioListCreate.as_view(), name='api_portfolio_list_create'),
    path('portfolio/<int:pk>/', PortfolioDetails.as_view(), name='api_portfolio_details'),

    # CustomLink CRUD
    path('administration/custom-link/', CustomLinkListCreate.as_view(), name='api_customlink_list_create'),
    path('administration/custom-link/<int:pk>/', CustomLinkDetails.as_view(), name='api_customlink_details'),

    # ApprovalWorkflow CRUD
    path('administration/approval/', ApprovalWorkflowListCreate.as_view(), name='api_approvalworkflow_list_create'),
    path('administration/approval/<int:pk>/', ApprovalWorkflowDetails.as_view(), name='api_approvalworkflow_details'),
    # ApprovalWorkflow update postion of steps
    path('administration/approval/<int:pk>/update_steps_position', ApprovalWorkflowUpdateStepsPosition.as_view(),
         name='api_approvalworkflow_update_steps_position'),

    # ApprovalStep CRUD
    path('administration/approval/<int:approval_workflow_id>/approval-step/', ApprovalStepListCreate.as_view(),
         name='api_approvalstep_list_create'),
    path('administration/approval/<int:approval_workflow_id>/approval-step/<int:pk>/', ApprovalStepDetails.as_view(),
         name='api_approvalstep_details'),
]
