from django.urls import reverse
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from guardian.decorators import permission_required

from service_catalog.filters.job_template_filter import JobTemplateFilter
from service_catalog.models import JobTemplate, TowerServer


class JobTemplateTable(tables.Table):
    compliant = TemplateColumn(template_name='custom_columns/job_template_compliant.html',
                               verbose_name="Squest compliant")
    actions = TemplateColumn(template_name='custom_columns/job_template_actions.html', orderable=False)

    class Meta:
        model = JobTemplate
        attrs = {"id": "job_template_table", "class": "table squest-pagination-tables"}
        fields = ("name", "compliant", "actions")


class JobTemplateListView(SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = JobTemplateTable
    model = JobTemplate
    template_name = 'generics/list.html'
    filterset_class = JobTemplateFilter

    @method_decorator(permission_required('service_catalog.view_jobtemplate'))
    def dispatch(self, *args, **kwargs):
        return super(JobTemplateListView, self).dispatch(*args, **kwargs)

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
        return context
