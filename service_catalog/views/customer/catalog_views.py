from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from service_catalog.forms import ServiceRequestForm
from service_catalog.mail_utils import send_mail_request_update
from service_catalog.models import Service


@login_required
def customer_list_service(request):
    services = Service.objects.all()
    return render(request, 'service_catalog/customer/catalog/service/service-list.html', {'services': services})


@login_required
def customer_service_request(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    parameters = {
        'service_id': service_id
    }

    if request.method == 'POST':
        
        form = ServiceRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            new_request = form.save()
            send_mail_request_update(target_request=new_request, user_applied_state=request.user)
            return redirect('service_catalog:customer_request_list')
    else:
        form = ServiceRequestForm(request.user, **parameters)

    return render(request, 'service_catalog/customer/catalog/service/service-request.html', {'form': form,
                                                                                             'service': target_service})
