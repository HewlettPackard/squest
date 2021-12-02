from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.support_filter import SupportFilter
from service_catalog.models import Support
from service_catalog.tables.support_tables import SupportTable


@method_decorator(login_required, name='dispatch')
class SupportListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = SupportTable
    model = Support
    template_name = 'generics/list.html'
    filterset_class = SupportFilter

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(SupportListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Supports"
        return context
