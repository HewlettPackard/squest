from django.urls import path

from service_catalog.api.admin.instance_api_views import InstanceList, InstanceDetails
from service_catalog.api.admin.job_template_fix_views import fix_ask_variables_on_launch

urlpatterns = [
    # admin urls
    path('admin/instance/', InstanceList.as_view(), name='api_admin_instance_list'),
    path('admin/instance/<int:pk>/', InstanceDetails.as_view(), name='api_admin_instance_details'),
    path('job_templates/<int:pk>/enable-extra-vars', fix_ask_variables_on_launch, name='fix_ask_variables_on_launch'),
]
