from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from service_catalog.forms import ServiceRequestForm
from service_catalog.models import Service, OperationType


@login_required
def customer_service_request(request, service_id, operation_id):
    target_service = get_object_or_404(Service, **{'id': service_id, 'enabled': True})
    create_operation_list = target_service.operations.filter(type=OperationType.CREATE)
    create_operation = get_object_or_404(create_operation_list, id=operation_id)

    target_service = get_object_or_404(Service, **{'id': service_id, 'enabled': True})
    parameters = {
        'service_id': service_id,
        'operation_id': operation_id
    }

    if request.method == 'POST':
        form = ServiceRequestForm(request.user, request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:request_list')
    else:
        form = ServiceRequestForm(request.user, **parameters)
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:portfolio_list')},
        {'text': target_service.name, 'url': ""},
    ]
    context = {'form': form, 'service': target_service, 'breadcrumbs': breadcrumbs,
               'icon_button': "fas fa-shopping-cart", 'text_button': "Request the service", 'color_button': "success"}
    return render(request, 'generics/generic_form.html', context)
