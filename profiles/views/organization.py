from Squest.utils.squest_views import *
from profiles.filters import OrganizationFilter
from profiles.filters.user_filter import UserFilter
from profiles.forms import OrganizationForm
from profiles.models import Organization, Team, Role, Quota
from profiles.tables import OrganizationTable, ScopeRoleTable, TeamTable, UserRoleTable
from profiles.tables.quota_table import QuotaTable
from service_catalog.models import Request, Instance
from service_catalog.tables.instance_tables import InstanceTable
from service_catalog.tables.request_tables import RequestTable


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
        context['users'] = UserRoleTable(self.object.users.all())
        context['quotas'] = QuotaTable(
            Quota.get_queryset_for_user(self.request.user, "profiles.view_quota") & self.object.quotas.distinct()
        )
        context['teams'] = TeamTable(
            Team.get_queryset_for_user(self.request.user, "profiles.view_team") & self.object.teams.distinct()
        )
        context['roles'] = ScopeRoleTable(
            Role.get_queryset_for_user(self.request.user, "profiles.view_role") & self.object.roles.distinct()
        )
        return context


class OrganizationCreateView(SquestCreateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationEditView(SquestUpdateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationDeleteView(SquestDeleteView):
    model = Organization
