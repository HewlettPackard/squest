from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from django.contrib.auth.models import User

from profiles.filters.user_filter import UserFilter
from profiles.models import BillingGroup


class UserByBillingGroupTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/user_by_group_actions.html', orderable=False)

    class Meta:
        model = User
        attrs = {"id": "user_by_billing_group_table", "class": "table squest-pagination-tables "}
        fields = ("username", "email", "actions")


class UserByBillingGroupListView(SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = UserByBillingGroupTable
    model = User
    template_name = 'generics/list.html'
    filterset_class = UserFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return User.objects.filter(billing_groups__id=self.kwargs.get('billing_group_id')).distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        billing_group_id = self.kwargs.get('billing_group_id')
        context['breadcrumbs'] = [
            {'text': 'Billing Groups', 'url': reverse('profiles:billing_group_list')},
            {'text': BillingGroup.objects.get(id=billing_group_id).name, 'url': ""},
            {'text': "Users", 'url': ""}
        ]
        context['html_button_path'] = "generics/buttons/manage_users.html"
        context['group_url'] = 'billing_group'
        context['group_id'] = billing_group_id
        return context
