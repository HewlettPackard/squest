from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from service_catalog.filters.support_filter import SupportFilter
from service_catalog.models import Support


@user_passes_test(lambda u: u.is_superuser)
def admin_support_list(request):
    support_filtered = SupportFilter(request.GET, queryset=Support.objects.all())
    return render(request, 'service_catalog/admin/support/support-list.html', {'supports': support_filtered})
