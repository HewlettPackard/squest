from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from django.contrib.auth.models import Group
from guardian.mixins import LoginRequiredMixin

from profiles.filters.group_filter import GroupFilter


class GroupTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/group_actions.html', orderable=False)
    users = TemplateColumn(template_name='custom_columns/group_users.html', orderable=False)

    class Meta:
        model = Group
        attrs = {"id": "group_table", "class": "table squest-pagination-tables "}
        fields = ("name", "users", "actions")


class GroupListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = GroupTable
    model = Group
    template_name = 'generics/list.html'
    filterset_class = GroupFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Groups"
        context['html_button_path'] = "generics/buttons/add_group.html"
        context['group_url'] = 'group'
        return context
