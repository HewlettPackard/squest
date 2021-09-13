from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn
from service_catalog.filters.global_hook_filter import GlobalHookFilter
from service_catalog.models import GlobalHook


class GlobalHookTable(tables.Table):
    state = TemplateColumn(template_name='custom_columns/global_hook_state.html')
    actions = TemplateColumn(template_name='custom_columns/global_hook_actions.html', orderable=False)

    class Meta:
        model = GlobalHook
        attrs = {"id": "global_hook_table", "class": "table squest-pagination-tables"}
        fields = ("name", "model", "state", "job_template", "actions")


class GlobalHookListView(SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = GlobalHookTable
    model = GlobalHook
    template_name = 'generics/list.html'
    filterset_class = GlobalHookFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Global hooks"
        context['html_button_path'] = "generics/buttons/create_global_hook.html"
        return context
