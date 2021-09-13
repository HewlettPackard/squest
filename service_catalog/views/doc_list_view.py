from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A
from service_catalog.filters.doc_filter import DocFilter
from service_catalog.models import Doc


class DocTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/doc_actions.html')
    services = TemplateColumn(template_name='custom_columns/doc_services.html', verbose_name="Linked services")
    title = LinkColumn("service_catalog:doc_show", args=[A("id")])

    class Meta:
        model = Doc
        attrs = {"id": "doc_table", "class": "table squest-pagination-tables"}
        fields = ("title", "services", "actions")


class DocListView(SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = DocTable
    model = Doc
    template_name = 'generics/list.html'
    filterset_class = DocFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Documentations"
        context['is_super'] = self.request.user.is_superuser
        context['html_button_path'] = "generics/buttons/manage_docs.html"
        return context
