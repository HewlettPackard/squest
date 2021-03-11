from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from service_catalog.forms import ServiceForm, AddServiceOperationForm, SurveySelectorForm
from service_catalog.models import Service, Operation


@user_passes_test(lambda u: u.is_superuser)
def service(request):
    services = Service.objects.all()
    return render(request, 'catalog/service-list.html', {'services': services})


@user_passes_test(lambda u: u.is_superuser)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            new_instance = form.save()
            # create the first operation of type create that link this service to a job template
            job_template = form.cleaned_data['job_template']
            Operation.objects.create(name=new_instance.name,
                                     service=new_instance,
                                     job_template=job_template)
            return redirect('settings_catalog')
    else:
        form = ServiceForm()

    return render(request, 'catalog/add_service.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def service_operations(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    operations = Operation.objects.filter(service=target_service)
    context = {
        "operations": operations,
        "service": target_service
    }
    return render(request, "catalog/service_operations.html", context)


@user_passes_test(lambda u: u.is_superuser)
def delete_service(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    if request.method == "POST":
        target_service.delete()
        return redirect(service)
    context = {
        "object": target_service
    }
    return render(request, "catalog/confirm_delete_service.html", context)


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
            return redirect('service_operations', service_id=target_service.id)
    else:
        form = AddServiceOperationForm()

    return render(request, 'catalog/add_service_operation.html', {'form': form,
                                                                  'service': target_service})


@user_passes_test(lambda u: u.is_superuser)
def delete_service_operation(request, service_id, operation_id):
    target_service = get_object_or_404(Service, id=service_id)
    target_operation = get_object_or_404(Operation, id=operation_id)
    if target_operation.type == "CREATE":
        # cannot delete a create type operation
        raise PermissionDenied
    if request.method == "POST":
        target_operation.delete()
        return redirect('service_operations', service_id=target_service.id)

    context = {
        "object": target_operation
    }
    return render(request, "catalog/confirm_delete_service_operation.html", context)


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
            return redirect('service_operations', service_id=target_service.id)
    else:
        form = SurveySelectorForm(**parameters)

    return render(request, 'catalog/service_operation_edit_survey.html', {'form': form,
                                                                          'service': target_service,
                                                                          'operation': target_operation})
