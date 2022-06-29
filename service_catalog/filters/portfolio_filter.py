from service_catalog.models import Portfolio
from Squest.utils.squest_filter import SquestFilter


class PortfolioFilter(SquestFilter):
    class Meta:
        model = Portfolio
        fields = ['name', 'parent_portfolio']
