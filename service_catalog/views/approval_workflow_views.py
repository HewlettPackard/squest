from django.shortcuts import get_object_or_404

from Squest.utils.squest_table import SquestRequestConfig
from Squest.utils.squest_views import SquestListView, SquestDetailView, SquestCreateView, SquestUpdateView, \
    SquestDeleteView, SquestConfirmView
from profiles.models import Scope, Organization, Team
from profiles.tables import ApprovalWorkflowPreviewTable
from service_catalog.filters.approval_workflow_filter import ApprovalWorkflowFilter
from service_catalog.forms.approval_workflow_form import ApprovalWorkflowForm, ApprovalWorkflowFormEdit
from service_catalog.models import ApprovalWorkflow, Request
from service_catalog.tables.approval_workflow_table import ApprovalWorkflowTable
from service_catalog.tables.request_tables import RequestTablesForApprovalWorkflow


class ApprovalWorkflowListView(SquestListView):
    table_class = ApprovalWorkflowTable
    model = ApprovalWorkflow
    filterset_class = ApprovalWorkflowFilter


class ApprovalWorkflowDetailView(SquestDetailView):
    model = ApprovalWorkflow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)

        context["request_table"] = RequestTablesForApprovalWorkflow(
            self.get_object()._get_request_using_workflow().prefetch_related(
                "user", "operation", "instance__requester", "instance__quota_scope", "instance__service",
                "operation__service", "approval_workflow_state", "approval_workflow_state__approval_workflow",
                "approval_workflow_state__current_step",
                "approval_workflow_state__current_step__approval_step", "approval_workflow_state__approval_step_states"
            ).filter(id__in=Request.get_queryset_for_user(self.request.user, "service_catalog.view_request")),
            hide_fields=["selection", "last_updated", "date_submitted"])
        config.configure(context['request_table'])

        context["scope_table"] = ApprovalWorkflowPreviewTable(
            Scope.objects.filter(id__in=Organization.get_queryset_for_user(self.request.user, 'profiles.view_organization').values_list("id",flat=True)) |
            Scope.objects.filter(id__in=Team.get_queryset_for_user(self.request.user, 'profiles.view_team')).values_list("id", flat=True)
        )
        config.configure(context['scope_table'])

        return context


class ApprovalWorkflowPreviewView(SquestDetailView):
    model = ApprovalWorkflow
    template_name = "service_catalog/approvalworkflow_preview.html"

    def get_permission_required(self):
        return "service_catalog.view_approvalworkflow"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scope = get_object_or_404(Scope, id=self.kwargs.get("scope_id"))
        context["current_workflow"] = scope.get_workflows().filter(operation=self.get_object().operation).first()
        context['scope'] = scope
        if scope.is_team:
            perm_add_approvers = "profiles.add_users_team"
        if scope.is_org:
            perm_add_approvers = "profiles.add_users_organization"
        context["can_add_approvers"] = self.request.user.has_perm(perm_add_approvers, scope)
        context["can_add_role"] = self.request.user.has_perm("profiles.add_role")
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': str(self.get_object()),
                'url': self.get_object().get_absolute_url()
            },
            {
                'text': scope,
                'url': ''
            },
        ]

        return context


class ApprovalWorkflowCreateView(SquestCreateView):
    model = ApprovalWorkflow
    form_class = ApprovalWorkflowForm


class ApprovalWorkflowEditView(SquestUpdateView):
    model = ApprovalWorkflow
    form_class = ApprovalWorkflowFormEdit


class ApprovalWorkflowDeleteView(SquestDeleteView):
    model = ApprovalWorkflow


class ApprovalWorkflowResetRequests(SquestConfirmView):
    model = ApprovalWorkflow
    permission_required = "service_catalog.re_submit_request"

    def form_valid(self, form):
        workflow = self.get_object()
        workflow.reset_all_approval_workflow_state()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_text'] = "Confirm reset to submitted of the following requests ?"
        context['button_text'] = 'Reset to submitted'
        context['breadcrumbs'].append(
            {
                'text': 'Reset to submitted',
                'url': ''
            }
        )
        context['detail_table'] = RequestTablesForApprovalWorkflow(
            self.get_object()._get_request_to_reset().prefetch_related(
                "user", "operation", "instance__requester", "instance__quota_scope", "instance__service",
                "operation__service", "approval_workflow_state", "approval_workflow_state__approval_workflow",
                "approval_workflow_state__current_step",
                "approval_workflow_state__current_step__approval_step", "approval_workflow_state__approval_step_states"
            ))
        context['detail_table'].exclude = ("selection",)
        config = SquestRequestConfig(self.request)
        config.configure(context['detail_table'])
        return context
