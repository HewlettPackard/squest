from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib.auth.models import User
from guardian.mixins import LoginRequiredMixin

from profiles.filters.user_with_billing_filter import UserBillingGroupsFilter
from profiles.tables.user_table import UserTable


class UserListView(LoginRequiredMixin, SingleTableMixin, FilterView):
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
