from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from service_catalog.models import Operation, Service, OperationType
from service_catalog.tables.operation_tables import CreateOperationTable


class CreateOperationListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = CreateOperationTable
    model = Operation
    template_name = 'generics/list.html'

    def get_table_data(self, **kwargs):
        return Operation.objects.filter(service__id=self.kwargs.get('service_id'), enabled=True, type=OperationType.CREATE)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.kwargs.get('service_id')
        context['service_id'] = service_id
        context['html_button_path'] = "generics/buttons/add_operation.html"
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
            {'text': Service.objects.get(id=service_id).name, 'url': ""},
            {'text': 'Create operations', 'url': ""},
        ]
        return context
