from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from service_catalog.models import Service


@login_required
def customer_list_service(request):
    services = Service.objects.all()
    return render(request, 'customer/catalog/service/service-list.html', {'services': services})
