from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user
from service_catalog.filters.request_filter import RequestFilter
from service_catalog.models import Request


class RequestTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/request_actions.html', orderable=False)
    state = TemplateColumn(template_name='custom_columns/request_state.html')
    operation__type = TemplateColumn(verbose_name="Type", template_name='custom_columns/request_operation_type.html')
    instance__name = LinkColumn("service_catalog:instance_details", args=[A("instance__id")],
                                verbose_name="Instance")

    def before_render(self, request):
        self.columns.hide('id')

        if request.user.is_superuser:
            self.columns.show('user')
        else:
            self.columns.hide('user')

    class Meta:
        model = Request
        attrs = {"id": "request_table", "class": "table squest-pagination-tables"}
        fields = ("id", "instance__name", "user", "date_submitted", "instance__service__name", "operation__name",
                  "operation__type", "state", "actions")


class RequestListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = RequestTable
    model = Request
    template_name = 'generics/list.html'
    ordering = '-date_submitted'

    filterset_class = RequestFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        if self.request.user.is_superuser:
            return Request.objects.all().distinct() & filtered
        else:
            return get_objects_for_user(self.request.user, 'service_catalog.view_request').distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_super"] = self.request.user.is_superuser
        context['title'] = "Requests"
        return context
