from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from service_catalog.forms import ServiceRequestForm
from service_catalog.models import Service, OperationType, Doc


@login_required
def customer_service_request(request, service_id, operation_id):
    target_service = get_object_or_404(Service, **{'id': service_id, 'enabled': True})
    create_operation_list = target_service.operations.filter(
        enabled=True, type=OperationType.CREATE,
        is_admin_operation__in=[False, request.user.is_superuser]
    )
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
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
        {'text': target_service.name, 'url': ""},
    ]
    docs = Doc.objects.filter(operations__service_id__in=[create_operation.id])
    context = {'form': form, 'service': target_service, 'breadcrumbs': breadcrumbs,
               'icon_button': "fas fa-shopping-cart", 'text_button': "Request the service",
               'color_button': "success",
               'docs': docs}
    return render(request, 'service_catalog/customer/generic_list_with_docs.html', context)
