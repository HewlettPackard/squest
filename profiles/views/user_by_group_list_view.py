from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from django.contrib.auth.models import User, Group
from guardian.mixins import LoginRequiredMixin

from profiles.filters.user_filter import UserFilter


class UserByGroupTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/user_by_group_actions.html', orderable=False)

    class Meta:
        model = User
        attrs = {"id": "user_by_group_table", "class": "table squest-pagination-tables "}
        fields = ("username", "email", "actions")


class UserByGroupListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = UserByGroupTable
    model = User
    template_name = 'generics/list.html'
    filterset_class = UserFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return User.objects.filter(groups__id=self.kwargs.get('group_id')).distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = Group.objects.get(id=self.kwargs.get('group_id'))
        context['breadcrumbs'] = [
            {'text': 'Groups', 'url': reverse('profiles:group_list')},
            {'text': group.name, 'url': ""},
            {'text': "Users", 'url': ""}
        ]
        context['html_button_path'] = "generics/buttons/manage_users.html"
        context['app_name'] = 'profiles'
        context['object_name'] = 'group'
        context['object_id'] = group.id
        context['object'] = group
        return context
