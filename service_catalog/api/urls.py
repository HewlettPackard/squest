from django.urls import path

from service_catalog.api.admin.instance_api_views import InstanceList, InstanceDetails
from service_catalog.api.admin.job_template_api_views import JobTemplateDetails, JobTemplateList, \
    TowerServerJobTemplateList
from service_catalog.api.admin.tower_server_api_views import TowerServerList, TowerServerDetails
from service_catalog.api.operation_api_views import OperationListCreate, OperationDetails, InstanceOperationList
from service_catalog.api.request_api_views import RequestList, RequestDetails, ServiceRequestListCreate, \
    OperationRequestCreate
from service_catalog.api.service_api_views import ServiceListCreate, ServiceDetails

urlpatterns = [
    # admin urls
    path('admin/instance/', InstanceList.as_view(), name='api_admin_instance_list'),
    path('admin/instance/<int:pk>/', InstanceDetails.as_view(), name='api_admin_instance_details'),
    path('instance/<int:instance_id>/operation/', InstanceOperationList.as_view(),
         name='api_instance_operation_list'),
    path('instance/<int:instance_id>/operation/<int:operation_id>/request/', OperationRequestCreate.as_view(),
         name='api_operation_request_create'),
    path('admin/job_template/', JobTemplateList.as_view(), name='api_admin_job_template_list'),
    path('admin/job_template/<int:pk>/', JobTemplateDetails.as_view(), name='api_admin_job_template_details'),
    path('request/', RequestList.as_view(), name='api_request_list'),
    path('request/<int:pk>/', RequestDetails.as_view(), name='api_request_details'),
    path('service/', ServiceListCreate.as_view(), name='api_service_list_create'),
    path('service/<int:pk>/', ServiceDetails.as_view(), name='api_service_details'),
    path('service/<int:service_id>/operation/', OperationListCreate.as_view(), name='api_operation_list_create'),
    path('service/<int:service_id>/operation/<int:pk>/', OperationDetails.as_view(), name='api_operation_details'),
    path('service/<int:pk>/request/', ServiceRequestListCreate.as_view(), name='api_service_request_list_create'),
    path('tower/', TowerServerList.as_view(), name='api_tower_server_list_create'),
    path('tower/<int:pk>/', TowerServerDetails.as_view(), name='api_tower_server_details'),
    path('tower/<int:tower_server_id>/job_template/', TowerServerJobTemplateList.as_view(), name='api_tower_server_job_template_list'),
]
