from Squest.utils.squest_table import SquestRequestConfig

from Squest.utils.squest_views import *
from profiles.filters import OrganizationFilter
from profiles.filters.user_filter import UserFilter
from profiles.forms import OrganizationForm
from profiles.models import Organization, Team
from profiles.tables import OrganizationTable, ScopeRoleTable, TeamTable, UserRoleTable
from profiles.tables.quota_table import QuotaTable
from service_catalog.tables.approval_workflow_table import ApprovalWorkflowPreviewTable


class OrganizationListView(SquestListView):
    model = Organization
    filterset_class = OrganizationFilter
    table_class = OrganizationTable
    ordering = 'name'


class OrganizationDetailView(SquestDetailView):
    model = Organization
    filterset_class = UserFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)
        if self.request.user.has_perm("profiles.view_users_organization", self.get_object()):
            context['users'] = UserRoleTable(self.object.users.all(), prefix="user-")
        else:
            context['users'] = UserRoleTable(self.object.users.filter(id=self.request.user.id), prefix="user-")
        config.configure(context['users'])

        if self.request.user.has_perm("profiles.view_quota", self.get_object()):
            context['quotas'] = QuotaTable(self.object.quotas.distinct(), hide_fields=["scope"], prefix="quota-")
            config.configure(context['quotas'])

        context['teams'] = TeamTable(
            Team.get_queryset_for_user(self.request.user, "profiles.view_team") & self.object.teams.distinct(),
            hide_fields=('org',), prefix="team-"
        )
        config.configure(context['teams'])
        if self.request.user.has_perm("service_catalog.view_approvalworkflow"):
            context["workflows"] = ApprovalWorkflowPreviewTable(self.get_object().get_workflows(), prefix="workflow-",
                                                         hide_fields=["enabled", "actions", "scopes"])
            config.configure(context["workflows"])
        context['roles'] = ScopeRoleTable(self.object.roles.distinct())
        config.configure(context['roles'])

        return context


class OrganizationCreateView(SquestCreateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationEditView(SquestUpdateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationDeleteView(SquestDeleteView):
    model = Organization
