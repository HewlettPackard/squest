from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.service_filter import ServiceFilter
from service_catalog.models import Service
from service_catalog.tables.service_tables import ServiceTable


class ServiceListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = ServiceTable
    model = Service
    template_name = 'generics/list.html'
    filterset_class = ServiceFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Service.objects.all()
        return Service.objects.filter(enabled=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:portfolio_list')},
            {'text': 'Services', 'url': ''}
        ]
        if self.request.user.is_superuser:
            context['html_button_path'] = "generics/buttons/create_service.html"
        return context
