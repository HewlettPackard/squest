from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from service_catalog.forms import ServiceForm, AddServiceOperationForm, SurveySelectorForm, EditServiceForm
from service_catalog.models import Service, Operation
from service_catalog.models.operations import OperationType


@user_passes_test(lambda u: u.is_superuser)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            new_service = form.save()
            new_service.create_provisioning_operation(form.cleaned_data['job_template'])
            return redirect('service_catalog:service_list')
    else:
        form = ServiceForm()
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': 'Create a new service', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'service_catalog/admin/service/service-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def delete_service(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    if request.method == "POST":
        target_service.delete()
        return redirect('service_catalog:manage_services')
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': ""},
    ]
    context = {
        'object': target_service,
        'breadcrumbs': breadcrumbs
    }
    return render(request,
                  "service_catalog/admin/service/service-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def edit_service(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)

    form = EditServiceForm(request.POST or None, request.FILES or None, instance=target_service)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:manage_services')
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': ""},
    ]
    context = {'form': form, 'service': target_service, 'breadcrumbs': breadcrumbs, 'action': 'edit'}
    return render(request,
                  'service_catalog/admin/service/service-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def add_service_operation(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = AddServiceOperationForm(request.POST)
        if form.is_valid():
            form.service_id = target_service.id
            new_operation = form.save(commit=False)
            new_operation.service = target_service
            new_operation.save()
            return redirect('service_catalog:service_operations', service_id=target_service.id)
    else:
        form = AddServiceOperationForm()
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': reverse('service_catalog:service_operations', args=[service_id])},
        {'text': 'Create a new operation', 'url': ""},
    ]
    context = {'form': form, 'service': target_service, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request,
                  'service_catalog/admin/service/operation/operation-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def delete_service_operation(request, service_id, operation_id):
    target_service = get_object_or_404(Service, id=service_id)
    target_operation = get_object_or_404(Operation, id=operation_id)
    if target_operation.type == OperationType.CREATE:
        # cannot delete a create type operation
        raise PermissionDenied
    if request.method == "POST":
        target_operation.delete()
        return redirect('service_catalog:service_operations', service_id=target_service.id)
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': reverse('service_catalog:service_operations', args=[service_id])},
        {'text': target_operation.name, 'url': ""},
    ]
    context = {
        'operation': target_operation,
        'service': target_service,
        'breadcrumbs': breadcrumbs
    }
    return render(request,
                  "service_catalog/admin/service/operation/operation-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def edit_service_operation(request, service_id, operation_id):
    target_service = get_object_or_404(Service, id=service_id)
    target_operation = get_object_or_404(Operation, id=operation_id)

    form = AddServiceOperationForm(request.POST or None, instance=target_operation)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:service_operations', service_id=target_service.id)
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': reverse('service_catalog:service_operations', args=[service_id])},
        {'text': target_operation.name, 'url': ""},
    ]
    context = {'form': form,
               'service': target_service,
               'operation': target_operation,
               'breadcrumbs': breadcrumbs,
               'action': 'edit'
               }
    return render(request,
                  'service_catalog/admin/service/operation/operation-edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def service_operation_edit_survey(request, service_id, operation_id):
    target_service = get_object_or_404(Service, id=service_id)
    target_operation = get_object_or_404(Operation, id=operation_id)
    parameters = {
        'operation_id': operation_id
    }
    if request.method == 'POST':
        form = SurveySelectorForm(request.POST, **parameters)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:service_operations', service_id=target_service.id)
    else:
        form = SurveySelectorForm(**parameters)
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': reverse('service_catalog:service_operations', args=[service_id])},
        {'text': target_operation.name, 'url': ""},
    ]
    context = {'form': form,
               'service': target_service,
               'operation': target_operation,
               'breadcrumbs': breadcrumbs}
    return render(request,
                  'service_catalog/admin/service/operation/operation-edit-survey.html', context)
