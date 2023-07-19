from django.db.models import CharField, IntegerField, ForeignKey, CASCADE

from Squest.utils.squest_model import SquestModel
from service_catalog.models import TowerServer


class Inventory(SquestModel):
    class Meta:
        unique_together = ('tower_id', 'tower_server',)
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    name = CharField(max_length=100)
    tower_id = IntegerField()
    tower_server = ForeignKey(TowerServer,
                              on_delete=CASCADE,
                              related_name="inventories",
                              related_query_name="inventory")
