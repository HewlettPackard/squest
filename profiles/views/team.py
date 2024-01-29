from Squest.utils.squest_table import SquestRequestConfig

from Squest.utils.squest_views import *
from profiles.filters.team_filter import TeamFilter
from profiles.forms.team_forms import TeamForm
from profiles.models.organization import Organization
from profiles.models.team import Team
from profiles.tables import UserRoleTable, ScopeRoleTable, TeamTable
from profiles.tables.quota_table import QuotaTable
from service_catalog.tables.approval_workflow_table import ApprovalWorkflowPreviewTable


def get_organization_breadcrumbs(team):
    breadcrumbs = [
        {'text': "Organization", 'url': reverse(f'profiles:organization_list')},
        {'text': team.org, 'url': team.org.get_absolute_url()},
    ]
    return breadcrumbs


class TeamListView(SquestListView):
    model = Team
    filterset_class = TeamFilter
    table_class = TeamTable
    ordering = 'name'


class TeamDetailView(SquestDetailView):
    model = Team

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = SquestRequestConfig(self.request)
        context['breadcrumbs'] = get_organization_breadcrumbs(self.object) + context['breadcrumbs']
        if self.request.user.has_perm("profiles.view_users_team", self.get_object()):
            context['users'] = UserRoleTable(self.object.users.all(), prefix="user-")
        else:
            context['users'] = UserRoleTable(self.object.users.filter(id=self.request.user.id), prefix="user-")
        config.configure(context['users'])

        if self.request.user.has_perm("profiles.view_quota", self.get_object()):
            context['quotas'] = QuotaTable(self.object.quotas.distinct(), hide_fields=["scope"], prefix="quota-")
            config.configure(context['quotas'])

        context['roles'] = ScopeRoleTable(self.object.roles.distinct(), prefix="role-")
        config.configure(context['roles'])

        if self.request.user.has_perm("service_catalog.view_approvalworkflow"):
            context["workflows"] = ApprovalWorkflowPreviewTable(self.get_object().get_workflows(), prefix="workflow-",
                                                         hide_fields=["enabled", "actions", "scopes"])
            config.configure(context["workflows"])

        return context


class TeamCreateView(SquestCreateView):
    model = Team
    form_class = TeamForm

    def get_initial(self):
        initial = super().get_initial()
        initial["org"] = f"{self.request.GET.get('org')}"
        return initial.copy()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only organizations for which a team can be created are listed.
        form.fields["org"].queryset = Organization.get_queryset_for_user(self.request.user, "profiles.add_team")
        return form

    def has_permission(self):
        # Permission is checked through the "org" field.
        return True


class TeamEditView(SquestUpdateView):
    model = Team
    form_class = TeamForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_organization_breadcrumbs(self.object) + context['breadcrumbs']
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only organizations for which a team can be created are listed.
        form.fields["org"].queryset = Organization.get_queryset_for_user(self.request.user, "profiles.add_team")
        return form


class TeamDeleteView(SquestDeleteView):
    model = Team

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = get_organization_breadcrumbs(self.object) + context['breadcrumbs']
        return context
