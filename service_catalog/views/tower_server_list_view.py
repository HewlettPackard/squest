from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.decorators import permission_required
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.tower_server_filter import TowerServerFilter
from service_catalog.models import TowerServer
from service_catalog.tables.tower_server_tables import TowerServerTable


class TowerServerListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = TowerServerTable
    model = TowerServer
    template_name = 'generics/list.html'
    filterset_class = TowerServerFilter

    @method_decorator(permission_required('service_catalog.view_towerserver'))
    def dispatch(self, *args, **kwargs):
        return super(TowerServerListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Tower/AWX"
        context['html_button_path'] = "generics/buttons/add_tower_server.html"
        return context
