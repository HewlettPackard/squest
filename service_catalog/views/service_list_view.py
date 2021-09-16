from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.service_filter import ServiceFilter
from service_catalog.models import Service


class ServiceTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/service_actions.html', orderable=False)
    enabled = TemplateColumn(template_name='custom_columns/boolean_check.html')
    operations = TemplateColumn(template_name='custom_columns/service_operations.html',
                                verbose_name="Operations", orderable=False)

    class Meta:
        model = Service
        attrs = {"id": "service_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "enabled", "operations", "actions")


class ServiceListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = ServiceTable
    model = Service
    template_name = 'generics/list.html'
    filterset_class = ServiceFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Service catalog"
        context['html_button_path'] = "generics/buttons/create_service.html"
        return context
