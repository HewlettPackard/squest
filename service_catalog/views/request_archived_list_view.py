from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user
from service_catalog.filters.request_filter import RequestArchivedFilter
from service_catalog.models import Request
from service_catalog.tables.request_tables import RequestTable


class RequestArchivedListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = RequestTable
    model = Request
    template_name = 'generics/list.html'
    ordering = '-date_submitted'

    filterset_class = RequestArchivedFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        if self.request.user.is_superuser:
            return Request.objects.all().distinct() & filtered
        else:
            return get_objects_for_user(self.request.user, 'service_catalog.view_request').distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['html_button_path'] = 'generics/buttons/delete_button.html'
            context['action_url'] = reverse('service_catalog:request_bulk_delete_confirm')
        context['breadcrumbs'] = [
            {'text': 'Requests', 'url': reverse('service_catalog:request_list')},
            {'text': 'Archived requests', 'url': ""}
        ]
        return context
