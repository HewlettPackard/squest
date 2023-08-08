from django.db.models import CharField, IntegerField, ForeignKey, CASCADE

from Squest.utils.squest_model import SquestModel
from service_catalog.models import AnsibleController


class Inventory(SquestModel):
    class Meta:
        unique_together = ('remote_id', 'ansible_controller',)
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    name = CharField(max_length=100)
    remote_id = IntegerField()
    ansible_controller = ForeignKey(AnsibleController,
                                    on_delete=CASCADE,
                                    related_name="inventories",
                                    related_query_name="inventory")
