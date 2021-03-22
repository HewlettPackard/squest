from django.urls import path

from service_catalog.api.admin.instance_api_views import InstanceList, InstanceDetails

urlpatterns = [
    # admin urls
    path('admin/instance/', InstanceList.as_view(), name='api_admin_instance_list'),
    path('admin/instance/<int:pk>/', InstanceDetails.as_view(), name='api_admin_instance_details'),
]
