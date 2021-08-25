from django.urls import path

from service_catalog.api.admin.instance_api_views import InstanceList, InstanceDetails
from service_catalog.api.admin.job_template_fix_views import JobTemplateFix

urlpatterns = [
    # admin urls
    path('admin/instance/', InstanceList.as_view(), name='api_admin_instance_list'),
    path('admin/instance/<int:pk>/', InstanceDetails.as_view(), name='api_admin_instance_details'),
    path('job_templates/<int:pk>/fix', JobTemplateFix.as_view(), name='fix_ask_variables_on_launch'),
]
