from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django_celery_results.models import TaskResult

from service_catalog import tasks
from service_catalog.forms import TowerServerForm
from service_catalog.models import TowerServer, JobTemplate
from service_catalog.serializers import TaskResultSerializer


@permission_required('service_catalog.view_towerserver')
def list_tower(request):
    tower_servers = TowerServer.objects.all()
    return render(request, 'service_catalog/settings/tower/tower-list.html', {'tower_servers': tower_servers})


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
    return render(request, 'service_catalog/settings/tower/tower-create.html', {'form': form})


@permission_required('service_catalog.change_towerserver')
def sync_tower(request, tower_id):
    if request.method == 'POST':
        task = tasks.sync_tower.delay(tower_id)
        task_result = TaskResult(task_id=task.task_id)
        task_result.save()
        return JsonResponse({"task_id": task_result.id}, status=202)


@permission_required('service_catalog.view_taskresult')
def get_task_result(request, task_id):
    task_result = TaskResult.objects.get(id=task_id)
    serialized_task = TaskResultSerializer(task_result)
    return JsonResponse(serialized_task.data, status=202)


@permission_required('service_catalog.view_jobtemplate')
def tower_job_templates_list(request, tower_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    job_templates = JobTemplate.objects.filter(tower_server=tower_server)
    context = {
        "job_templates": job_templates
    }
    return render(request, "service_catalog/settings/tower/job_templates/job-templates-list.html", context)


@permission_required('service_catalog.delete_towerserver')
def delete_tower(request, tower_id):
    obj = get_object_or_404(TowerServer, id=tower_id)
    if request.method == "POST":
        obj.delete()
        return redirect('service_catalog:list_tower')
    context = {
        "object": obj
    }
    return render(request, "service_catalog/settings/tower/tower-delete.html", context)


@permission_required('service_catalog.delete_jobtemplate')
def delete_job_template(request, tower_id, job_template_id):
    obj = get_object_or_404(JobTemplate, id=job_template_id)
    obj.delete()
    return redirect('service_catalog:tower_job_templates_list', tower_id=tower_id)


@permission_required('service_catalog.change_towerserver')
def update_tower(request, tower_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    form = TowerServerForm(request.POST or None, instance=tower_server)
    if form.is_valid():
        form.save()
        return redirect('service_catalog:list_tower')
    return render(request, 'service_catalog/settings/tower/tower-edit.html', {'form': form, 'tower_server': tower_server})
