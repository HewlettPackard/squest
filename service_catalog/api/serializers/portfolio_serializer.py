from rest_framework.serializers import ModelSerializer

from service_catalog.models import Portfolio


class PortfolioSerializer(ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('id', 'name', 'description', 'parent_portfolio', 'image', 'portfolio_list', 'service_list')
        read_only_fields = ('id', 'portfolio_list', 'service_list')
