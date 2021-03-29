from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.models import Instance


@user_passes_test(lambda u: u.is_superuser)
def admin_instance_list(request):
    f = InstanceFilter(request.GET, queryset=Instance.objects.all())
    return render(request, 'admin/instance/instance-list.html', {'filter': f})
