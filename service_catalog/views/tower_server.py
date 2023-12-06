import logging
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django_celery_results.models import TaskResult
from Squest.utils.squest_table import SquestRequestConfig

from Squest.utils.squest_views import SquestListView, SquestCreateView, SquestDeleteView, SquestUpdateView, \
    SquestDetailView
from service_catalog import tasks
from service_catalog.filters.tower_server_filter import TowerServerFilter
from service_catalog.forms import TowerServerForm
from service_catalog.models import TowerServer
from service_catalog.tables.job_template_tables import JobTemplateTable
from service_catalog.tables.tower_server_tables import TowerServerTable

logger = logging.getLogger(__name__)


class TowerServerListView(SquestListView):
    table_class = TowerServerTable
    model = TowerServer
    filterset_class = TowerServerFilter


class TowerServerDetailView(SquestDetailView):
    model = TowerServer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)
        context["jobtemplate_table"] = JobTemplateTable(self.object.jobtemplate_set.all(), prefix="jobtemplate-")
        config.configure(context['jobtemplate_table'])

        return context


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
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    tower_server = get_object_or_404(TowerServer, pk=tower_id)
    if not request.user.has_perm('service_catalog.sync_towerserver', tower_server):
        raise PermissionDenied
    logger.debug(f'Celery task: "towerserver_sync" will be send with tower_id: {tower_id} and job_template_id: {pk}')
    task = tasks.towerserver_sync.delay(tower_id, pk)
    task_result = TaskResult(task_id=task.task_id)
    task_result.save()
    return JsonResponse({"task_id": task_result.id}, status=202)
