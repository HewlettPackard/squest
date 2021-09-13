from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from django.contrib.auth.models import User
from profiles.filters.user_with_billing_filter import UserBillingGroupsFilter


class UserTable(tables.Table):
    billing_groups = TemplateColumn(template_name='custom_columns/user_billing_groups.html', orderable=False)

    class Meta:
        model = User
        attrs = {"id": "user_table", "class": "table squest-pagination-tables "}
        fields = ("username", "email", "billing_groups")


class UserListView(SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = UserTable
    model = User
    template_name = 'generics/list.html'
    filterset_class = UserBillingGroupsFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Users"
        context['html_button_path'] = "generics/buttons/manage_all_users.html"
        return context
