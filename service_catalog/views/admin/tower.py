from django.contrib.auth.decorators import permission_required, login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_celery_results.models import TaskResult

from service_catalog import tasks
from service_catalog.forms import TowerServerForm
from service_catalog.models import TowerServer, JobTemplate, Operation, OperationType


@login_required
@permission_required('service_catalog.add_towerserver')
def add_tower(request):
    if request.method == 'POST':
        form = TowerServerForm(request.POST)
        if form.is_valid():
            new_tower = form.save()
            new_tower.sync()
            return redirect('service_catalog:list_tower')
    else:
        form = TowerServerForm()
    breadcrumbs = [
        {'text': 'Tower/AWX', 'url': reverse('service_catalog:list_tower')},
        {'text': 'Create a new server', 'url': ""}
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'generics/generic_form.html', context)


@login_required
@permission_required('service_catalog.change_towerserver')
def sync_tower(request, tower_id, job_template_id=None):
    if request.method == 'POST':
        task = tasks.sync_tower.delay(tower_id, job_template_id)
        task_result = TaskResult(task_id=task.task_id)
        task_result.save()
        return JsonResponse({"task_id": task_result.id}, status=202)


@login_required
@permission_required('service_catalog.delete_towerserver')
def delete_tower(request, tower_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    if request.method == "POST":
        tower_server.delete()
        return redirect('service_catalog:list_tower')
    breadcrumbs = [
        {'text': 'Tower/AWX', 'url': reverse('service_catalog:list_tower')},
        {'text': tower_server.name, 'url': ""}
    ]
    context = {
        "tower_server": tower_server,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/tower/tower-delete.html", context)


@login_required
@permission_required('service_catalog.delete_jobtemplate')
def delete_job_template(request, tower_id, job_template_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    job_template = get_object_or_404(JobTemplate, id=job_template_id)
    if request.method == 'POST':
        job_template.delete()
        return redirect('service_catalog:tower_job_templates_list', tower_id=tower_id)
    args = {
        "tower_id": tower_server.id,
        "job_template_id": job_template.id,
    }
    breadcrumbs = [
        {'text': 'Tower/AWX', 'url': reverse('service_catalog:list_tower')},
        {'text': tower_server.name, 'url': ""},
        {'text': 'Job templates', 'url': reverse('service_catalog:tower_job_templates_list', args=[tower_id])},
        {'text': job_template.name, 'url': ""},
        {'text': 'Delete', 'url': ""}
    ]
    warning_service_disabled = ' - This service will be disabled'
    operations = Operation.objects.filter(job_template=job_template)
    context = {
        'breadcrumbs': breadcrumbs,
        'confirm_text': mark_safe(f"Confirm deletion of <strong>{job_template.name}</strong>?"),
        'action_url': reverse('service_catalog:delete_job_template', kwargs=args),
        'button_text': 'Delete',
        'details': {'warning_sentence': 'Warning: some services/operations are still using this job template:',
                    'details_list': [
                        f"Service: \"{operation.service.name}\" / Operation: \"{operation.name}\"{warning_service_disabled if operation.type == OperationType.CREATE else ''}."
                        for operation in operations]
                    } if operations else None
    }
    return render(request, 'generics/confirm-delete-template.html', context=context)


@login_required
@permission_required('service_catalog.view_jobtemplate')
def job_template_details(request, tower_id, job_template_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    job_template = get_object_or_404(JobTemplate, id=job_template_id)
    breadcrumbs = [
        {'text': 'Tower/AWX', 'url': reverse('service_catalog:list_tower')},
        {'text': tower_server.name, 'url': ""},
        {'text': 'Job templates', 'url': reverse('service_catalog:tower_job_templates_list', args=[tower_id])},
        {'text': job_template.name, 'url': ""},
    ]
    context = {
        "job_template": job_template,
        'breadcrumbs': breadcrumbs
    }
    return render(request, "service_catalog/admin/tower/job_templates/job-template-details.html", context=context)


@login_required
@permission_required('service_catalog.view_jobtemplate')
def job_template_compliancy(request, tower_id, job_template_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    job_template = get_object_or_404(JobTemplate, id=job_template_id)
    breadcrumbs = [
        {'text': 'Tower/AWX', 'url': reverse('service_catalog:list_tower')},
        {'text': tower_server.name, 'url': ""},
        {'text': 'Job templates', 'url': reverse('service_catalog:tower_job_templates_list', args=[tower_id])},
        {'text': job_template.name, 'url': ""},
        {'text': 'Compliancy', 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'compliancy_details': job_template.get_compliancy_details(),
    }
    return render(request, "service_catalog/admin/tower/job_templates/job-template-compliancy.html", context)


@login_required
@permission_required('service_catalog.change_towerserver')
def update_tower(request, tower_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    form = TowerServerForm(request.POST or None, instance=tower_server)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:list_tower')
    breadcrumbs = [
        {'text': 'Tower/AWX', 'url': reverse('service_catalog:list_tower')},
        {'text': tower_server.name, 'url': ""}
    ]
    context = {'form': form, 'tower_server': tower_server, 'breadcrumbs': breadcrumbs, 'action': 'edit'}
    return render(request, 'generics/generic_form.html', context)
