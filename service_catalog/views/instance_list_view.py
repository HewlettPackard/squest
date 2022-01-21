from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user

from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.models import Instance
from service_catalog.tables.instance_tables import InstanceTable


class InstanceListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = InstanceTable
    model = Instance
    template_name = 'generics/list.html'
    filterset_class = InstanceFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        if self.request.user.is_superuser:
            return Instance.objects.all().distinct().order_by("-date_available") & filtered
        else:
            return get_objects_for_user(self.request.user, 'service_catalog.view_instance').distinct().order_by("-date_available") & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Instances"
        return context
