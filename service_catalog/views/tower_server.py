from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django_celery_results.models import TaskResult

from Squest.utils.squest_views import SquestListView, SquestCreateView, SquestDeleteView, SquestUpdateView
from service_catalog import tasks
from service_catalog.filters.tower_server_filter import TowerServerFilter
from service_catalog.forms import TowerServerForm
from service_catalog.models import TowerServer
from service_catalog.tables.tower_server_tables import TowerServerTable


class TowerServerListView(SquestListView):
    table_class = TowerServerTable
    model = TowerServer
    filterset_class = TowerServerFilter


class TowerServerCreateView(SquestCreateView):
    model = TowerServer
    form_class = TowerServerForm
    success_url = reverse_lazy("service_catalog:towerserver_list")

    def form_valid(self, form):
        form = super(TowerServerCreateView, self).form_valid(form)
        self.object.sync()
        return form


class TowerServerDeleteView(SquestDeleteView):
    model = TowerServer


class TowerServerEditView(SquestUpdateView):
    model = TowerServer
    form_class = TowerServerForm
    success_url = reverse_lazy("service_catalog:towerserver_list")


@login_required
def towerserver_sync(request, tower_id, pk=None):
    tower_server = get_object_or_404(TowerServer, pk=tower_id)
    if not request.user.has_perm('service_catalog.sync_towerserver', tower_server):
        raise PermissionDenied
    if request.method == 'POST':
        task = tasks.towerserver_sync.delay(tower_id, pk)
        task_result = TaskResult(task_id=task.task_id)
        task_result.save()
        return JsonResponse({"task_id": task_result.id}, status=202)
