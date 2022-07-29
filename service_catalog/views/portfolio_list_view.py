from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from guardian.mixins import LoginRequiredMixin

from service_catalog.filters.portfolio_filter import PortfolioFilter
from service_catalog.models import Portfolio
from service_catalog.tables.portfolio_tables import PortfolioTable


@method_decorator(login_required, name='dispatch')
class PortfolioListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_pagination = {'per_page': 10}
    table_class = PortfolioTable
    model = Portfolio
    template_name = 'generics/list.html'
    filterset_class = PortfolioFilter
    queryset = Portfolio.objects.all()

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super(PortfolioListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'text': 'Service catalog', 'url': reverse('service_catalog:service_catalog_list')},
            {'text': 'Portfolios', 'url': ''}
        ]
        if self.request.user.is_superuser:
            context['html_button_path'] = "generics/buttons/generic_add_button.html"
            context['app_name'] = "service_catalog"
            context['object_name'] = "portfolio"
        return context
