from django.db.models import Model, CharField, ManyToManyField
from django.db.models.signals import m2m_changed

from resource_tracker.models.resource_group_attribute_definition import ResourceGroupAttributeDefinition
from service_catalog import tasks


class Quota(Model):
    name = CharField(max_length=100, blank=False, unique=True)
    attribute_definitions = ManyToManyField(
        ResourceGroupAttributeDefinition,
        blank=True,
        help_text="The attribute definitions linked to this quota.",
        related_name="quota",
        related_query_name="quota",
        verbose_name="Attribute Definition"
    )


def attribute_definitions_changed(sender, instance, **kwargs):
    tasks.quota_update_consumed.delay(instance.id)


m2m_changed.connect(attribute_definitions_changed, sender=Quota.attribute_definitions.through)
