from Squest.utils.squest_views import *
from profiles.filters.team_filter import TeamFilter
from profiles.forms.team_forms import TeamForm
from profiles.models.organization import Organization
from profiles.models.team import Team
from profiles.tables import UserRoleTable, ScopeRoleTable, TeamTable
from profiles.tables.quota_table import QuotaTable


class TeamListView(SquestListView):
    model = Team
    filterset_class = TeamFilter
    table_class = TeamTable
    ordering = 'name'


class TeamDetailView(SquestDetailView):
    model = Team

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
                                     {'text': 'Organization', 'url': reverse('profiles:organization_list')},
                                     {'text': f'{self.object.org}', 'url': reverse('profiles:organization_details',
                                                                                   kwargs={'pk': self.object.org.id})},
                                 ] + context['breadcrumbs']
        if self.request.user.has_perm("profiles.view_users_team", self.get_object()):
            context['users'] = UserRoleTable(self.object.users.all())

        if self.request.user.has_perm("profiles.view_quota", self.get_object()):
            context['quotas'] = QuotaTable(self.object.quotas.distinct(), hide_fields=["scope"]
                                           )
        context['roles'] = ScopeRoleTable(self.object.roles.distinct())
        return context


class TeamCreateView(SquestCreateView):
    model = Team
    form_class = TeamForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["org"].queryset = Organization.get_queryset_for_user(self.request.user, "profiles.add_team")
        return form

    def has_permission(self):
        return True


class TeamEditView(SquestUpdateView):
    model = Team
    form_class = TeamForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["org"].queryset = Organization.get_queryset_for_user(self.request.user, "profiles.add_team")
        return form


class TeamDeleteView(SquestDeleteView):
    model = Team
