from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django_celery_results.models import TaskResult

from Squest.utils.squest_views import SquestListView, SquestCreateView, SquestDeleteView, SquestUpdateView, \
    SquestDetailView
from service_catalog import tasks
from service_catalog.filters.ansible_controller_filter import AnsibleControllerFilter
from service_catalog.forms import AnsibleControllerForm
from service_catalog.models import AnsibleController
from service_catalog.tables.job_template_tables import JobTemplateTable
from service_catalog.tables.ansible_controller_tables import AnsibleControllerTable


class AnsibleControllerListView(SquestListView):
    table_class = AnsibleControllerTable
    model = AnsibleController
    filterset_class = AnsibleControllerFilter


class AnsibleControllerDetailView(SquestDetailView):
    model = AnsibleController

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jobtemplate_table"] = JobTemplateTable(self.object.jobtemplate_set.all())
        return context

class AnsibleControllerCreateView(SquestCreateView):
    model = AnsibleController
    form_class = AnsibleControllerForm
    success_url = reverse_lazy("service_catalog:ansiblecontroller_list")

    def form_valid(self, form):
        form = super(AnsibleControllerCreateView, self).form_valid(form)
        self.object.sync()
        return form


class AnsibleControllerDeleteView(SquestDeleteView):
    model = AnsibleController


class AnsibleControllerEditView(SquestUpdateView):
    model = AnsibleController
    form_class = AnsibleControllerForm
    success_url = reverse_lazy("service_catalog:ansiblecontroller_list")


@login_required
def ansiblecontroller_sync(request, ansible_controller_id, pk=None):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    ansible_controller = get_object_or_404(AnsibleController, pk=ansible_controller_id)
    if not request.user.has_perm('service_catalog.sync_ansiblecontroller', ansible_controller):
        raise PermissionDenied
    task = tasks.ansiblecontroller_sync.delay(ansible_controller_id, pk)
    task_result = TaskResult(task_id=task.task_id)
    task_result.save()
    return JsonResponse({"task_id": task_result.id}, status=202)
