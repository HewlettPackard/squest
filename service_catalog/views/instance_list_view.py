from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A
from guardian.shortcuts import get_objects_for_user
from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.models import Instance


class InstanceTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/instance_actions.html', orderable=False)
    state = TemplateColumn(template_name='custom_columns/instance_state.html')
    service__name = TemplateColumn(template_name='custom_columns/instance_type.html', verbose_name="Type")
    request = TemplateColumn(template_name='custom_columns/instance_requests.html', verbose_name="Requests")
    opened_support_count = TemplateColumn(template_name='custom_columns/instance_opened_support.html',
                                          verbose_name="Opened support")
    name = LinkColumn("service_catalog:customer_instance_details", args=[A("id")], verbose_name="Name")

    def before_render(self, request):
        if request.user.is_superuser:
            self.columns.show('opened_support_count')
        else:
            self.columns.hide('opened_support_count')

    class Meta:
        model = Instance
        attrs = {"id": "instance_table", "class": "table squest-pagination-tables"}
        fields = ("name", "service__name", "request", "state", "opened_support_count", "spoc", "actions")


class InstanceListView(SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = InstanceTable
    model = Instance
    template_name = 'generics/list.html'
    filterset_class = InstanceFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        if self.request.user.is_superuser:
            return Instance.objects.all().distinct() & filtered
        else:
            return get_objects_for_user(self.request.user, 'service_catalog.view_instance').distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_super"] = self.request.user.is_superuser
        context['title'] = "Instances"
        return context
