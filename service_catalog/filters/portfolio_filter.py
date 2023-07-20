from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import Portfolio


class PortfolioFilter(SquestFilter):
    class Meta:
        model = Portfolio
        fields = ['name', 'parent_portfolio']
