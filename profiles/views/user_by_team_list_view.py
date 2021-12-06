from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from django.contrib.auth.models import User
from guardian.decorators import permission_required_or_403
from guardian.mixins import LoginRequiredMixin

from profiles.filters.user_filter import UserFilter
from profiles.models import UserRoleBinding
from profiles.models.team import Team


class UserByTeamTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/user_by_group_actions.html', orderable=False)
    role = TemplateColumn(template_name='custom_columns/user_role_team.html', orderable=False)

    class Meta:
        model = User
        attrs = {"id": "user_by_team_table", "class": "table squest-pagination-tables "}
        fields = ("username", "email", "role", "actions")


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required_or_403('profiles.view_team', (Team, 'id', 'team_id')), name='dispatch')
class UserByTeamListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = UserByTeamTable
    model = User
    template_name = 'generics/list.html'
    filterset_class = UserFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        team = Team.objects.get(id=self.kwargs.get('team_id'))
        return team.get_all_users().distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_id = self.kwargs.get('team_id')
        team = Team.objects.get(id=team_id)
        roles = dict()
        for user in team.get_all_users():
            roles[user.username] = [binding.role.name for binding in UserRoleBinding.objects.filter(
                user=user,
                content_type=ContentType.objects.get_for_model(Team),
                object_id=team.id)]
        context['breadcrumbs'] = [
            {'text': 'Teams', 'url': reverse('profiles:team_list')},
            {'text': Team.objects.get(id=team_id).name, 'url': ""},
            {'text': "Users", 'url': ""}
        ]
        context['roles'] = roles
        context['add_button_url'] = "team"
        context['html_button_path'] = "profiles/user_role/change-users-in-role.html"
        context['app_name'] = 'profiles'
        context['object_name'] = 'team'
        context['group_id'] = team_id
        context['object_id'] = team_id
        return context
