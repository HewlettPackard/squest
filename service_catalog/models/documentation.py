from django.db.models import Model, CharField, ManyToManyField
from martor.models import MartorField

from . import Service


class Doc(Model):
    title = CharField(max_length=100)
    content = MartorField()
    services = ManyToManyField(
        Service,
        blank=True,
        help_text="Services linked to this doc.",
        related_name="docs",
        related_query_name="doc",
    )

    def __str__(self):
        return self.title
