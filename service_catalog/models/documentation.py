from django.db.models import CharField, ManyToManyField
from martor.models import MartorField

from Squest.utils.squest_model import SquestModel


class Doc(SquestModel):
    title = CharField(max_length=100)
    content = MartorField()
    services = ManyToManyField(
        'service_catalog.Service',
        blank=True,
        help_text="Services linked to this doc.",
        related_name="docs",
        related_query_name="doc",
    )
    operations = ManyToManyField(
        'service_catalog.Operation',
        blank=True,
        help_text="Operations linked to this doc.",
        related_name="docs",
        related_query_name="doc",
    )
    when = CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.title
