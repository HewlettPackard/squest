from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django_celery_results.models import TaskResult

from service_catalog import tasks
from service_catalog.forms import TowerServerForm
from service_catalog.models import TowerServer, JobTemplate
from service_catalog.serializers import TaskResultSerializer


@user_passes_test(lambda u: u.is_superuser)
def tower(request):
    tower_servers = TowerServer.objects.all()

    return render(request, 'settings/tower/tower-list.html', {'tower_servers': tower_servers})


@user_passes_test(lambda u: u.is_superuser)
def add_tower(request):
    if request.method == 'POST':
        form = TowerServerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tower')
    else:
        form = TowerServerForm()

    return render(request, 'settings/tower/tower-create.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def sync_tower(request, tower_id):
    if request.POST:
        task = tasks.sync_tower.delay(tower_id)
        task_result = TaskResult(task_id=task.task_id)
        task_result.save()

        return JsonResponse({"task_id": task_result.id}, status=202)


@user_passes_test(lambda u: u.is_superuser)
def get_task_result(request, task_id):
    task_result = TaskResult.objects.get(id=task_id)
    serialized_task = TaskResultSerializer(task_result)
    return JsonResponse(serialized_task.data, status=202)


@user_passes_test(lambda u: u.is_superuser)
def delete_tower(request, tower_id):
    obj = get_object_or_404(TowerServer, id=tower_id)
    if request.method == "POST":
        obj.delete()
        return redirect(tower)
    context = {
        "object": obj
    }
    return render(request, "settings/tower/tower-delete.html", context)


@user_passes_test(lambda u: u.is_superuser)
def tower_job_templates(request, tower_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    job_templates = JobTemplate.objects.filter(tower_server=tower_server)
    context = {
        "job_templates": job_templates
    }
    return render(request, "settings/tower/job_templates/job-templates-list.html", context)


@user_passes_test(lambda u: u.is_superuser)
def delete_job_template(request, tower_id, job_template_id):
    obj = get_object_or_404(JobTemplate, id=job_template_id)
    obj.delete()
    return redirect('tower_job_templates', tower_id=tower_id)


def update_tower(request, tower_id):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    form = TowerServerForm(request.POST or None, instance=tower_server)
    if form.is_valid():
        form.save()
        return redirect('tower')

    return render(request, 'settings/tower/tower-edit.html', {'form': form, 'tower_server': tower_server})
