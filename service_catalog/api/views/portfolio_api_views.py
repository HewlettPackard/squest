from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from service_catalog.api.serializers.portfolio_serializer import PortfolioSerializer
from service_catalog.filters.portfolio_filter import PortfolioFilter
from service_catalog.models.portfolio import Portfolio


class PortfolioDetails(RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsAdminUser()]
        return [IsAuthenticated()]


class PortfolioListCreate(ListCreateAPIView):
    filterset_class = PortfolioFilter
    serializer_class = PortfolioSerializer
    queryset = Portfolio.objects.all()

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsAdminUser()]
        return [IsAuthenticated()]
