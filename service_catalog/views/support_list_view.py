from guardian.shortcuts import get_objects_for_user

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.support_filter import SupportFilter
from service_catalog.models import Support
from service_catalog.tables.support_tables import SupportTable


class SupportListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = SupportTable
    model = Support
    template_name = 'generics/list.html'
    filterset_class = SupportFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return Support.get_queryset_for_user(self.request.user, 'service_catalog.request_support_on_instance').distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
