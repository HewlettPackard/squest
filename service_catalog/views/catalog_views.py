from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from Squest.utils.squest_views import SquestPermissionDenied
from service_catalog.forms import ServiceRequestForm
from service_catalog.models import Service, OperationType, Doc


@login_required
def request_service(request, service_id, operation_id):
    target_service = get_object_or_404(Service, id=service_id, enabled=True)
    create_operation_list = target_service.operations.filter(
        enabled=True, type=OperationType.CREATE
    )
    create_operation = get_object_or_404(create_operation_list, id=operation_id)

    if create_operation.is_admin_operation and not request.user.has_perm('service_catalog.admin_request_on_service', create_operation):
        raise SquestPermissionDenied(permission='service_catalog.admin_request_on_service')
    if not create_operation.is_admin_operation and not request.user.has_perm('service_catalog.request_on_service', create_operation):
        raise SquestPermissionDenied(permission='service_catalog.request_on_service')

    parameters = {
        'service': target_service,
        'operation': create_operation
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
    context = {'form': form, 'service': target_service, 'breadcrumbs': breadcrumbs,
               'icon_button': "fas fa-shopping-cart", 'text_button': "Request the service",
               'color_button': "success",
               'docs': create_operation.docs.all()}
    return render(request, 'service_catalog/customer/generic_list_with_docs.html', context)
