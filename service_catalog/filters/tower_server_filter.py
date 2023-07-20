from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import TowerServer


class TowerServerFilter(SquestFilter):
    class Meta:
        model = TowerServer
        fields = ['name', 'host']
