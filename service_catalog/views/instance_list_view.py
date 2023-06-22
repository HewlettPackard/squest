from django.urls import reverse
from guardian.shortcuts import get_objects_for_user

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.models import Instance
from service_catalog.tables.instance_tables import InstanceTable


class InstanceListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = InstanceTable
    model = Instance
    template_name = 'generics/list.html'
    filterset_class = InstanceFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        return Instance.get_queryset_for_user(
            self.request.user,
            'service_catalog.view_instance').distinct().order_by("-date_available") & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['html_button_path'] = 'generics/buttons/delete_button.html'
            context['action_url'] = reverse('service_catalog:instance_bulk_delete_confirm')
        return context
