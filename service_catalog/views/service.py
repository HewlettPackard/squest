from Squest.utils.squest_views import *
from service_catalog.filters.service_filter import ServiceFilter
from service_catalog.forms import ServiceForm

from service_catalog.models import Service
from service_catalog.tables.service_tables import ServiceTable


class ServiceListView(SquestListView):
    table_class = ServiceTable
    model = Service
    filterset_class = ServiceFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': ''}
        ]
        return context


class ServiceCreateView(SquestCreateView):
    model = Service
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': reverse('service_catalog:service_list')},
            {'text': 'New service', 'url': ""},
        ]
        context['multipart'] = True
        return context

    def get_success_url(self):
        return reverse("service_catalog:operation_create", kwargs={"service_id": self.object.id})


class ServiceEditView(SquestUpdateView):
    model = Service
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': reverse('service_catalog:service_list')},
            {'text': self.get_object(), 'url': ""},
        ]
        context['multipart'] = True
        return context


class ServiceDeleteView(SquestDeleteView):
    model = Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': reverse('service_catalog:service_list')},
            {'text': self.get_object(), 'url': ""},
        ]
        return context
