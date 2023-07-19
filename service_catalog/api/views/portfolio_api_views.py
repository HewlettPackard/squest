from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from service_catalog.api.serializers.portfolio_serializer import PortfolioSerializer
from service_catalog.filters.portfolio_filter import PortfolioFilter
from service_catalog.models.portfolio import Portfolio


class PortfolioDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer


class PortfolioListCreate(SquestListCreateAPIView):
    filterset_class = PortfolioFilter
    serializer_class = PortfolioSerializer
    queryset = Portfolio.objects.all()
