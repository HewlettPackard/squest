from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A
from service_catalog.filters.support_filter import SupportFilter
from service_catalog.models import Support


class SupportTable(tables.Table):
    state = TemplateColumn(template_name='custom_columns/support_state.html')
    title = LinkColumn("service_catalog:admin_instance_support_details", args=[A("instance__id"), A("id")])
    instance__name = LinkColumn("service_catalog:admin_instance_details", args=[A("instance__id")],
                                verbose_name="Instance")

    class Meta:
        model = Support
        attrs = {"id": "support_table", "class": "table squest-pagination-tables"}
        fields = ("title", "instance__name", "user_open", "date_opened", "state")


class SupportListView(SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = SupportTable
    model = Support
    template_name = 'generics/list.html'
    filterset_class = SupportFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Supports"
        return context
