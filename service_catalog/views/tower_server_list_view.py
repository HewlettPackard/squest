from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A
from guardian.decorators import permission_required
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.tower_server_filter import TowerServerFilter
from service_catalog.models import TowerServer


class TowerServerTable(tables.Table):
    name = LinkColumn("service_catalog:update_tower", args=[A("id")])
    host = TemplateColumn(template_name='custom_columns/tower_server_host.html')
    jobtemplate = TemplateColumn(template_name='custom_columns/tower_server_job_templates.html',
                                 verbose_name="Job templates")
    actions = TemplateColumn(template_name='custom_columns/tower_server_actions.html', orderable=False)

    class Meta:
        model = TowerServer
        attrs = {"id": "tower_server_table", "class": "table squest-pagination-tables"}
        fields = ("name", "host", "jobtemplate", "actions")


class TowerServerListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = TowerServerTable
    model = TowerServer
    template_name = 'generics/list.html'
    filterset_class = TowerServerFilter

    @method_decorator(permission_required('service_catalog.view_towerserver'))
    def dispatch(self, *args, **kwargs):
        return super(TowerServerListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Tower/AWX"
        context['html_button_path'] = "generics/buttons/add_tower_server.html"
        return context
