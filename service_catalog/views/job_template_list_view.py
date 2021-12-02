from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.decorators import permission_required
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.job_template_filter import JobTemplateFilter
from service_catalog.models import JobTemplate, TowerServer
from service_catalog.tables.job_template_tables import JobTemplateTable


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('service_catalog.view_jobtemplate'), name='dispatch')
class JobTemplateListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = JobTemplateTable
    model = JobTemplate
    template_name = 'generics/list.html'
    filterset_class = JobTemplateFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return JobTemplate.objects.filter(tower_server__id=self.kwargs.get('tower_id')).distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tower_server_id = self.kwargs.get('tower_id')
        context['breadcrumbs'] = [
            {'text': 'Tower/AWX', 'url': reverse('service_catalog:list_tower')},
            {'text': TowerServer.objects.get(id=tower_server_id).name, 'url': ""},
            {'text': 'Job templates', 'url': ""},
        ]
        context['tower_id'] = tower_server_id
        return context
