from django.db.models import Model, CharField, IntegerField, ForeignKey, CASCADE

from service_catalog.models import TowerServer


class Credential(Model):
    name = CharField(max_length=100)
    tower_id = IntegerField()
    tower_server = ForeignKey(TowerServer,
                              on_delete=CASCADE,
                              related_name="credentials",
                              related_query_name="credential"
                              )

    class Meta:
        unique_together = ('tower_id', 'tower_server',)
