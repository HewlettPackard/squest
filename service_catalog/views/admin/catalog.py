from django.contrib.auth.decorators import user_passes_test
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from service_catalog.forms import ServiceOperationForm, ServiceForm
from service_catalog.models import Service, Operation
from service_catalog.models.tower_survey_field import TowerSurveyField, TowerSurveyFieldForm


@user_passes_test(lambda u: u.is_superuser)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            return redirect(reverse('service_catalog:add_service_operation', kwargs={"service_id": service.id}))
    else:
        form = ServiceForm()
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': 'Create a new service', 'url': ""},
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create', 'multipart': True}
    return render(request, 'generics/generic_form.html', context)


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

    form = ServiceForm(request.POST or None, request.FILES or None, instance=target_service)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:manage_services')
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': ""},
    ]
    context = {'form': form, 'service': target_service, 'breadcrumbs': breadcrumbs, 'action': 'edit', 'multipart': True}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def add_service_operation(request, service_id):
    target_service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceOperationForm(request.POST, service=target_service)
        if form.is_valid():
            form.save()
            return redirect('service_catalog:service_operations', service_id=target_service.id)
    else:
        form = ServiceOperationForm(service=target_service)
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': reverse('service_catalog:service_operations', args=[service_id])},
        {'text': 'Create a new operation', 'url': ""},
    ]
    context = {'form': form, 'service': target_service, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def delete_service_operation(request, service_id, operation_id):
    target_service = get_object_or_404(Service, id=service_id)
    target_operation = get_object_or_404(Operation, id=operation_id)
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

    form = ServiceOperationForm(request.POST or None, instance=target_operation, service=target_service)
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
               'action': 'edit',
               'html_button_path': 'service_catalog/admin/service/operation/operation-button-edit-survey.html'
               }
    return render(request, 'generics/generic_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def service_operation_edit_survey(request, service_id, operation_id):
    target_service = get_object_or_404(Service, id=service_id)
    target_operation = get_object_or_404(Operation, id=operation_id)
    survey_selector_form_set = modelformset_factory(TowerSurveyField,
                                                    form=TowerSurveyFieldForm,
                                                    extra=0)
    formset = survey_selector_form_set(queryset=target_operation.tower_survey_fields.all())

    if request.method == 'POST':
        formset = survey_selector_form_set(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('service_catalog:service_operations', service_id=target_service.id)

    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
        {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
        {'text': target_service.name, 'url': reverse('service_catalog:service_operations', args=[service_id])},
        {'text': target_operation.name, 'url': ""},
    ]
    context = {'formset': formset,
               'service': target_service,
               'operation': target_operation,
               'breadcrumbs': breadcrumbs}
    return render(request,
                  'service_catalog/admin/service/operation/operation-edit-survey.html', context)
