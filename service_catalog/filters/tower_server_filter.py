from service_catalog.models import TowerServer
from Squest.utils.squest_filter import SquestFilter


class TowerServerFilter(SquestFilter):
    class Meta:
        model = TowerServer
        fields = ['name', 'host']
