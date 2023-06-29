from django.urls import reverse

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.request_filter import RequestFilter
from service_catalog.models import Request
from service_catalog.tables.request_tables import RequestTable


class RequestListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = RequestTable
    model = Request
    template_name = 'generics/list.html'
    ordering = '-date_submitted'

    filterset_class = RequestFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return Request.get_queryset_for_user(self.request.user, 'service_catalog.view_request').distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = "generics/buttons/request-archived-list.html"
        if self.request.user.is_superuser:
            context['action_url'] = reverse('service_catalog:request_bulk_delete_confirm')
        return context
