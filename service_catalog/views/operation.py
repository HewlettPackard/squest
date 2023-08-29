from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from Squest.utils.squest_views import *
from service_catalog.filters.operation_filter import OperationFilter, OperationFilterLimited
from service_catalog.forms import ServiceOperationForm
from service_catalog.models import Operation, Service, OperationType
from service_catalog.tables.operation_tables import OperationTable, CreateOperationTable


class OperationListView(SquestListView):
    model = Operation
    filterset_class = OperationFilter
    table_class = OperationTable

    def get_generic_url_kwargs(self):
        return {'service_id': self.kwargs.get('service_id')}

    def get_queryset(self):
        return super().get_queryset().filter(service__id=self.kwargs.get('service_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': reverse('service_catalog:service_list')},
            {'text': Service.objects.get(id=self.kwargs.get('service_id')), 'url': ""},
            {'text': 'Operations', 'url': ""},
        ]
        return context


class OperationCreateView(SquestCreateView):
    model = Operation
    form_class = ServiceOperationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        kwargs['service'] = self.service
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': reverse('service_catalog:service_list')},
            {'text': self.service, 'url': reverse('service_catalog:operation_list', args=[self.service.id])},
            {'text': 'Create a new operation', 'url': ""},
        ]
        return context


class OperationEditView(SquestUpdateView):
    model = Operation
    form_class = ServiceOperationForm

    def get_success_url(self):
        return self.get_object().service.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['service'] = self.get_object().service
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': reverse('service_catalog:service_list')},
            {'text': self.get_object().service,
             'url': reverse('service_catalog:operation_list', args=[self.get_object().service.id])},
            {'text': self.get_object(), 'url': ""},
        ]
        return context


class OperationDeleteView(SquestDeleteView):
    model = Operation

    def get_generic_url_kwargs(self):
        return {'service_id': self.kwargs.get('service_id')}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': reverse('service_catalog:service_list')},
            {'text': self.get_object().service,
             'url': reverse('service_catalog:operation_list', args=[self.get_object().service.id])},
            {'text': self.get_object(), 'url': ""},
        ]
        return context


class CreateOperationListView(SquestListView):
    model = Operation
    filterset_class = OperationFilterLimited
    table_class = CreateOperationTable

    def get_generic_url(self, action):
        return ""

    def get_queryset(self):
        service_id = self.kwargs.get('service_id')
        return Operation.get_queryset_for_user(self.request.user, "service_catalog.view_operation").filter(
            service__id=service_id,
            enabled=True, type=OperationType.CREATE,
        )

    def dispatch(self, request, *args, **kwargs):
        if self.get_queryset().count() == 1:
            return redirect('service_catalog:request_service', service_id=self.kwargs.get('service_id'),
                            operation_id=self.get_queryset().first().id)
        return super(CreateOperationListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.kwargs.get('service_id')
        context['service_id'] = service_id
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': Service.objects.get(id=service_id).name, 'url': ""},
            {'text': 'Create operations', 'url': ""},
        ]
        context['html_button_path'] = ""
        context['add_url'] = ""
        return context
