from Squest.utils.squest_views import SquestListView, SquestDetailView, SquestCreateView, SquestUpdateView, \
    SquestDeleteView
from service_catalog.filters.approval_workflow_filter import ApprovalWorkflowFilter
from service_catalog.forms.approval_workflow_form import ApprovalWorkflowForm
from service_catalog.models import ApprovalWorkflow
from service_catalog.tables.approval_workflow_table import ApprovalWorkflowTable


class ApprovalWorkflowListView(SquestListView):
    table_class = ApprovalWorkflowTable
    model = ApprovalWorkflow
    filterset_class = ApprovalWorkflowFilter


class ApprovalWorkflowDetailView(SquestDetailView):
    model = ApprovalWorkflow


class ApprovalWorkflowCreateView(SquestCreateView):
    model = ApprovalWorkflow
    form_class = ApprovalWorkflowForm


class ApprovalWorkflowEditView(SquestUpdateView):
    model = ApprovalWorkflow
    form_class = ApprovalWorkflowForm


class AttributeDefinitionDeleteView(SquestDeleteView):
    model = ApprovalWorkflow
    template_name = 'generics/delete.html'
