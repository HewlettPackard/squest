from Squest.utils.squest_views import SquestListView
from service_catalog.filters.doc_filter import DocFilter
from service_catalog.models import Doc
from service_catalog.tables.doc_tables import DocTable


class DocListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = DocTable
    model = Doc
    template_name = 'generics/list.html'
    filterset_class = DocFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_super'] = self.request.user.is_superuser
        context['html_button_path'] = "generics/buttons/manage_docs.html"
        return context
