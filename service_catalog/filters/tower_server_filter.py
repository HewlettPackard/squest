from service_catalog.models import TowerServer
from utils.squest_filter import SquestFilter


class TowerServerFilter(SquestFilter):
    class Meta:
        model = TowerServer
        fields = ['name', 'host']
