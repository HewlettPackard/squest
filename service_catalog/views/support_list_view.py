from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user

from service_catalog.filters.support_filter import SupportFilter
from service_catalog.models import Support
from service_catalog.tables.support_tables import SupportTable


class SupportListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = SupportTable
    model = Support
    template_name = 'generics/list.html'
    filterset_class = SupportFilter

    def get_table_data(self, **kwargs):
        filtered = super().get_table_data().distinct()
        if self.request.user.is_superuser:
            return Support.objects.all().distinct() & filtered
        else:
            instances = get_objects_for_user(self.request.user, 'service_catalog.request_support_on_instance').distinct()
            return Support.objects.filter(instance__in=instances).distinct() & filtered

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Supports"
        return context
