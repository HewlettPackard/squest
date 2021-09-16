from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from guardian.mixins import LoginRequiredMixin

from profiles.filters.billing_group_filter import BillingGroupFilter
from profiles.models import BillingGroup


class BillingGroupTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/group_actions.html', orderable=False)
    users = TemplateColumn(template_name='custom_columns/group_users.html', orderable=False)

    class Meta:
        model = BillingGroup
        attrs = {"id": "billing_group_table", "class": "table squest-pagination-tables "}
        fields = ("name", "users", "actions")


class BillingGroupListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = BillingGroupTable
    model = BillingGroup
    template_name = 'generics/list.html'
    filterset_class = BillingGroupFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Billing groups"
        context['html_button_path'] = "generics/buttons/add_group.html"
        context['group_url'] = 'billing_group'
        return context
