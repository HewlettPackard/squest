from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from Squest.utils.squest_views import *
from service_catalog.filters.job_template_filter import JobTemplateFilter
from service_catalog.models import TowerServer, JobTemplate, OperationType
from service_catalog.tables.job_template_tables import JobTemplateTable


class JobTemplateListView(SquestListView):
    table_class = JobTemplateTable
    model = JobTemplate
    filterset_class = JobTemplateFilter

    def get_queryset(self, **kwargs):
        return super(JobTemplateListView, self).get_queryset().filter(tower_server__id=self.kwargs.get('tower_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = ""
        context['breadcrumbs'] = [
            {'text': 'Controller', 'url': reverse('service_catalog:towerserver_list')},
            {'text': TowerServer.objects.get(id=self.kwargs.get('tower_id')).name, 'url': ""},
            {'text': 'Job templates', 'url': ""},
        ]
        return context


class JobTemplateDetailView(SquestDetailView):
    model = JobTemplate

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Ansible Controller', 'url': reverse('service_catalog:towerserver_list')},
            {'text': self.get_object().tower_server.name, 'url': ""},
            {'text': 'Job templates', 'url': reverse('service_catalog:jobtemplate_list', args=[self.get_object().tower_server.id])},
            {'text': self.get_object(), 'url': ""},
        ]
        return context


class JobTemplateDeleteView(SquestDeleteView):
    model = JobTemplate

    def get_generic_url_kwargs(self):
        return {'tower_id': self.get_object().tower_server.id}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        operations = self.get_object().operation_set.all()
        context['details'] = {
            'warning_sentence': 'Warning: some services/operations are still using this job template:',
            'details_list': [
                f"Service: \"{operation.service.name}\" / Operation: \"{operation.name}\"{' - This service will be disabled' if operation.type == OperationType.CREATE else ''}."
                for operation in operations]
        } if operations else None
        context['breadcrumbs'] = [
            {'text': 'Ansible Controller', 'url': reverse('service_catalog:towerserver_list')},
            {'text': self.get_object().tower_server.name, 'url': ""},
            {'text': 'Job templates',
             'url': reverse('service_catalog:jobtemplate_list', args=[self.get_object().tower_server.id])},
            {'text': self.get_object(), 'url': ""},
            {'text': 'Delete', 'url': ""}
        ]
        return context


@login_required
def job_template_compliancy(request, tower_id, pk):
    tower_server = get_object_or_404(TowerServer, id=tower_id)
    job_template = get_object_or_404(JobTemplate, id=pk)
    if not request.user.has_perm('service_catalog.view_jobtemplate', job_template):
        raise PermissionDenied
    breadcrumbs = [
        {'text': 'Ansible Controller', 'url': reverse('service_catalog:towerserver_list')},
        {'text': tower_server.name, 'url': ""},
        {'text': 'Job templates', 'url': reverse('service_catalog:jobtemplate_list', args=[tower_id])},
        {'text': job_template.name, 'url': ""},
        {'text': 'Compliancy', 'url': ""}
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'compliancy_details': job_template.get_compliancy_details(),
    }
    return render(request, "service_catalog/admin/tower/job_templates/job-template-compliancy.html", context)
