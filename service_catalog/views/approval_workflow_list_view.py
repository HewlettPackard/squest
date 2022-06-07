from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.approval_workflow_filter import ApprovalWorkflowFilter
from service_catalog.models.approval_workflow import ApprovalWorkflow
from service_catalog.tables.approval_workflow_table import ApprovalWorkflowTable


@method_decorator(login_required, name='dispatch')
class ApprovalWorkflowListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = ApprovalWorkflowTable
    model = ApprovalWorkflow
    template_name = 'generics/list.html'
    filterset_class = ApprovalWorkflowFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(ApprovalWorkflowListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Approvals"
        context['app_name'] = "service_catalog"
        context['object_name'] = "approval_workflow"
        context['html_button_path'] = "generics/buttons/generic_add_button.html"
        return context
