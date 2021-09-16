from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.operation_filter import OperationFilter
from service_catalog.models import Operation, Service


class OperationTable(tables.Table):
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    auto_accept = TemplateColumn(template_name='custom_columns/operation_boolean.html')
    auto_process = TemplateColumn(template_name='custom_columns/operation_boolean.html')
    survey = TemplateColumn(template_name='custom_columns/operation_survey.html', orderable=False)
    actions = TemplateColumn(template_name='custom_columns/operation_actions.html', orderable=False)

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "type", "job_template", "auto_accept", "auto_process", "process_timeout_second", "survey",
                  "actions")


class OperationListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = OperationTable
    model = Operation
    template_name = 'generics/list.html'
    filterset_class = OperationFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return Operation.objects.filter(service__id=self.kwargs.get('service_id')).distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.kwargs.get('service_id')
        context['service_id'] = service_id
        context['html_button_path'] = "generics/buttons/add_operation.html"
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
            {'text': 'Manage services', 'url': reverse('service_catalog:manage_services')},
            {'text': Service.objects.get(id=service_id).name, 'url': ""},
            {'text': 'Operations', 'url': ""},
        ]
        return context
