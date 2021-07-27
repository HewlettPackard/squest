from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from service_catalog.forms import ServiceForm, AddServiceOperationForm, SurveySelectorForm, EditServiceForm
from service_catalog.models import Service, Operation
from service_catalog.models.operations import OperationType


@user_passes_test(lambda u: u.is_superuser)
def service(request):
    services = Service.objects.all()
    return render(request, 'service_catalog/settings/catalog/service/service-list.html', {'services': services})


@user_passes_test(lambda u: u.is_superuser)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            new_service = form.save()
            # create the first operation of type create that link this service to a job template
            job_template = form.cleaned_data['job_template']
            Operation.objects.create(name=new_service.name,
                                     service=new_service,
                                     job_template=job_template)
            return redirect('service_catalog:service_list')
    else:
        form = ServiceForm()

    return render(request, 'service_catalog/settings/catalog/service/service-create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def service_operations(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    operations = Operation.objects.filter(service=target_service)
    context = {
        "operations": operations,
        "service": target_service
    }
    return render(request, "service_catalog/settings/catalog/service/operation/operation-list.html", context)


@user_passes_test(lambda u: u.is_superuser)
def delete_service(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    if request.method == "POST":
        target_service.delete()
        return redirect('service_catalog:service_list')
    context = {
        "object": target_service
    }
    return render(request, "service_catalog/settings/catalog/service/service-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def edit_service(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)

    form = EditServiceForm(request.POST or None, request.FILES or None, instance=target_service)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:service_list')

    return render(request, 'service_catalog/settings/catalog/service/service-edit.html', {'form': form,
                                                                                          'service': target_service})


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

    return render(request, 'service_catalog/settings/catalog/service/operation/operation-create.html', {'form': form,
                                                                                                        'service': target_service})


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

    context = {
        "operation": target_operation,
        "service": target_service
    }
    return render(request, "service_catalog/settings/catalog/service/operation/operation-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def edit_service_operation(request, service_id, operation_id):
    target_service = get_object_or_404(Service, id=service_id)
    target_operation = get_object_or_404(Operation, id=operation_id)

    form = AddServiceOperationForm(request.POST or None, instance=target_operation)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:service_operations', service_id=target_service.id)

    return render(request, 'service_catalog/settings/catalog/service/operation/operation-edit.html', {'form': form,
                                                                                                      'service': target_service,
                                                                                                      'operation': target_operation})


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

    context = {'form': form,
               'service': target_service,
               'operation': target_operation}
    return render(request, 'service_catalog/settings/catalog/service/operation/operation-edit-survey.html', context=context)
