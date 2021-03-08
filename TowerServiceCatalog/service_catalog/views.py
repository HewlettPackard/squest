from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django_celery_results.models import TaskResult
from rest_framework import status
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from . import tasks
from .forms import TowerServerForm
from .models import TowerServer
from .serializers import TaskResultSerializer


@login_required
def home(request):
    return render(request, 'home.html')


@user_passes_test(lambda u: u.is_superuser)
def tower(request):
    tower_servers = TowerServer.objects.all()

    return render(request, 'tower/tower-list.html', {'tower_servers': tower_servers})


@user_passes_test(lambda u: u.is_superuser)
def add_tower(request):
    if request.method == 'POST':
        form = TowerServerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tower')
    else:
        form = TowerServerForm()

    return render(request, 'tower/add_tower.html', {'form': form})


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
    # return JsonResponse({"task": task_result}, status=202)

    serialized_task = TaskResultSerializer(task_result)
    return JsonResponse(serialized_task.data, status=202)
