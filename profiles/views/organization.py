from Squest.utils.squest_views import *
from profiles.filters import OrganizationFilter
from profiles.filters.user_filter import UserFilter
from profiles.forms import OrganizationForm
from profiles.models import Organization
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
        context['users'] = UserRoleTable(self.object.users.all())
        context['teams'] = TeamTable(self.object.teams.all().distinct())
        context['roles'] = ScopeRoleTable(self.object.roles.all())
        context['quotas'] = QuotaTable(self.object.quotas.all())
        return context


class OrganizationCreateView(SquestCreateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationEditView(SquestUpdateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationDeleteView(SquestDeleteView):
    model = Organization
