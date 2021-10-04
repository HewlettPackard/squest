from django.urls import path

from service_catalog.api.admin.instance_api_views import InstanceList, InstanceDetails
from service_catalog.api.admin.job_template_api_views import JobTemplateDetails, JobTemplateList
from service_catalog.api.admin.request_api_views import RequestList, RequestDetails

urlpatterns = [
    # admin urls
    path('admin/instance/', InstanceList.as_view(), name='api_admin_instance_list'),
    path('admin/instance/<int:pk>/', InstanceDetails.as_view(), name='api_admin_instance_details'),
    path('admin/job_template/', JobTemplateList.as_view(), name='api_admin_job_template_list'),
    path('admin/job_template/<int:pk>/', JobTemplateDetails.as_view(), name='api_admin_job_template_details'),
    path('request/', RequestList.as_view(), name='api_admin_request_list'),
]
