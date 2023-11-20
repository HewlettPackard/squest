from django.shortcuts import redirect
from Squest.utils.squest_table import SquestRequestConfig

from Squest.utils.squest_views import *
from service_catalog.filters.operation_filter import OperationFilter, OperationFilterLimited
from service_catalog.forms import OperationForm
from service_catalog.models import Operation, Service, OperationType, ApprovalWorkflow
from service_catalog.tables.approval_workflow_table import ApprovalWorkflowTable
from service_catalog.tables.operation_tables import OperationTable, CreateOperationTable


def get_breadcrumbs_for_operation(operation):
    breadcrumbs = [
        {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
        {'text': 'Service', 'url': reverse('service_catalog:service_list')},
        {'text': operation.service, 'url': operation.service.get_absolute_url()},
        {'text': 'Operation', 'url': ''},
    ]
    if operation is not None:
        breadcrumbs.append({'text': operation, 'url': operation.get_absolute_url()})
    return breadcrumbs


class OperationListView(SquestListView):
    model = Operation
    filterset_class = OperationFilter
    table_class = OperationTable


class OperationCreateView(SquestCreateView):
    model = Operation
    form_class = OperationForm

    def get_initial(self):
        initial = super().get_initial()
        initial["service"] = f"{self.request.GET.get('service')}"
        return initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Operation', 'url': reverse('service_catalog:operation_list')},
            {'text': 'New operation', 'url': ""},
        ]
        return context


class OperationDetailView(SquestDetailView):
    model = Operation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)

        context['breadcrumbs'] = get_breadcrumbs_for_operation(self.get_object())
        context['extra_html_button_path'] = "service_catalog/buttons/operation_survey_button.html"
        if self.request.user.has_perm('service_catalog.view_approvalworkflow'):
            context['workflows_table'] = ApprovalWorkflowTable(
                ApprovalWorkflow.objects.filter(operation=self.get_object()), exclude=['operation'],
                prefix="operation-")
            config.configure(context['workflows_table'])

        return context


class OperationEditView(SquestUpdateView):
    model = Operation
    form_class = OperationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_breadcrumbs_for_operation(self.get_object())
        context['breadcrumbs'].append({'text': 'Edit', 'url': ''})
        return context


class OperationDeleteView(SquestDeleteView):
    model = Operation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_breadcrumbs_for_operation(self.get_object())
        context['breadcrumbs'].append({'text': 'Delete', 'url': ''})
        return context


class CreateOperationListView(SquestListView):
    model = Operation
    filterset_class = OperationFilterLimited
    table_class = CreateOperationTable

    def get_generic_url(self, action):
        return ""

    def get_queryset(self):
        return Operation.get_queryset_for_user(self.request.user, "service_catalog.view_operation").filter(
            service__id=self.kwargs.get('service_id'),
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
