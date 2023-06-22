from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.decorators import method_decorator

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.service_filter import ServiceFilter
from service_catalog.models import Service
from service_catalog.tables.service_tables import ServiceTable


@method_decorator(login_required, name='dispatch')
class ServiceListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = ServiceTable
    model = Service
    template_name = 'generics/list.html'
    filterset_class = ServiceFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(ServiceListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Service.objects.all()
        return Service.objects.filter(enabled=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Services', 'url': ''}
        ]
        if self.request.user.is_superuser:
            context['html_button_path'] = "generics/buttons/create_service.html"
        return context
