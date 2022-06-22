from django.shortcuts import redirect
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

    def get_queryset(self):
        return Operation.objects.filter(service__id=self.kwargs.get('service_id'), enabled=True, type=OperationType.CREATE)

    def dispatch(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if qs.count() == 1:
            return redirect('service_catalog:customer_service_request', service_id=self.kwargs.get('service_id'),
                            operation_id=qs.first().id)
        return super(CreateOperationListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.kwargs.get('service_id')
        context['service_id'] = service_id
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_list')},
            {'text': Service.objects.get(id=service_id).name, 'url': ""},
            {'text': 'Create operations', 'url': ""},
        ]
        return context
