from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user

from profiles.filters.team_filter import TeamFilter
from profiles.models.team import Team
from profiles.tables.team_table import TeamTable


class TeamListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = TeamTable
    model = Team
    template_name = 'generics/list.html'
    filterset_class = TeamFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        if self.request.user.is_superuser:
            return Team.objects.all().distinct() & filtered
        else:
            return get_objects_for_user(self.request.user, 'profiles.view_team').distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Teams"
        context['html_button_path'] = "generics/buttons/add_group.html"
        context['object_name'] = 'team'
        return context
