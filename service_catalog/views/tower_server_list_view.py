from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.tower_server_filter import TowerServerFilter
from service_catalog.models import TowerServer
from service_catalog.tables.tower_server_tables import TowerServerTable


@method_decorator(login_required, name='dispatch')
class TowerServerListView(SquestListView):
    table_pagination = {'per_page': 10}
    table_class = TowerServerTable
    model = TowerServer
    template_name = 'generics/list.html'
    filterset_class = TowerServerFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(TowerServerListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Controllers"
        context['html_button_path'] = "generics/buttons/add_tower_server.html"
        return context
