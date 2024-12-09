from Squest.utils.squest_views import *
from profiles.models import Permission
from service_catalog.filters.service_filter import ServiceFilter
from service_catalog.forms import ServiceForm

from service_catalog.models import Service, Operation, OperationType
from service_catalog.tables.operation_tables import OperationTable
from service_catalog.tables.service_tables import ServiceTable


def get_breadcrumbs_for_service(service=None):
    breadcrumbs = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Service', 'url': reverse('service_catalog:service_list')}
    ]
    if service is not None:
        breadcrumbs.append({'text': service, 'url': service.get_absolute_url()})
    return breadcrumbs

class ServiceListView(SquestListView):
    table_class = ServiceTable
    model = Service
    filterset_class = ServiceFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_breadcrumbs_for_service()
        return context

    def get_queryset(self):
        # get all create and enabled permission for current selected service
        all_permission_current_service = Permission.objects.filter(operation__enabled=True,
                                                                   operation__type__in=[
                                                                       OperationType.CREATE]).distinct()
        # Init empty queryset to be returned
        operation_qs = Operation.objects.none()
        for permission in all_permission_current_service.all():
            # add allowed operation for all service if the user has the permission
            operation_qs = operation_qs | Operation.get_queryset_for_user_filtered(self.request.user,
                                                                                   permission.permission_str)
        # restrict to only the selected service
        service_ids = operation_qs.filter(enabled=True,
                                           type__in=[OperationType.CREATE]).values_list('service__id', flat=True)
        return Service.objects.filter(id__in=service_ids)


class ServiceDetailView(SquestDetailView):
    model = Service
    filterset_class = ServiceFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_breadcrumbs_for_service(self.get_object())
        if self.request.user.has_perm("service_catalog.list_operation", self.object):
            context['operations_table'] = OperationTable(self.object.operations.all(), prefix="operation-")
        return context


class ServiceCreateView(SquestCreateView):
    model = Service
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_breadcrumbs_for_service()
        context['breadcrumbs'][1]['url'] = reverse('service_catalog:service_list')
        context['breadcrumbs'].append({'text': 'New service', 'url': ""})
        context['multipart'] = True
        return context

    def get_success_url(self):
        return reverse("service_catalog:operation_create")


class ServiceEditView(SquestUpdateView):
    model = Service
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_breadcrumbs_for_service(self.get_object())
        context['breadcrumbs'].append({'text': 'Edit', 'url': ''})
        context['multipart'] = True
        return context


class ServiceDeleteView(SquestDeleteView):
    model = Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_breadcrumbs_for_service(self.get_object())
        context['breadcrumbs'].append({'text': 'Delete', 'url': ''})
        return context
