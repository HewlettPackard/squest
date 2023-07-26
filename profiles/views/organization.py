from Squest.utils.squest_views import *
from profiles.filters import OrganizationFilter
from profiles.filters.user_filter import UserFilter
from profiles.forms import OrganizationForm
from profiles.models import Organization, Team, Role, Quota
from profiles.tables import OrganizationTable, ScopeRoleTable, TeamTable, UserRoleTable
from profiles.tables.quota_table import QuotaTable


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
        if self.request.user.has_perm("profiles.view_users_organization", self.get_object()):
            context['users'] = UserRoleTable(self.object.users.all())

        if self.request.user.has_perm("profiles.view_quota", self.get_object()):
            context['quotas'] = QuotaTable(self.object.quotas.distinct(), hide_fields=["scope"]
                                           )
        context['teams'] = TeamTable(
            Team.get_queryset_for_user(self.request.user, "profiles.view_team") & self.object.teams.distinct()
        )

        context['roles'] = ScopeRoleTable(self.object.roles.distinct())
        return context


class OrganizationCreateView(SquestCreateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationEditView(SquestUpdateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationDeleteView(SquestDeleteView):
    model = Organization
