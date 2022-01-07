from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class ResourceAttribute(models.Model):
    value = models.PositiveIntegerField(default=0)

    resource = models.ForeignKey('Resource',
                                 on_delete=models.CASCADE,
                                 related_name='attributes',
                                 related_query_name='attribute',
                                 null=True)

    attribute_type = models.ForeignKey('ResourceGroupAttributeDefinition',
                                       on_delete=models.CASCADE,
                                       related_name='attribute_types',
                                       related_query_name='attribute_type',
                                       null=True)

    def __str__(self):
        return str(self.value)


@receiver(post_save, sender=ResourceAttribute)
def on_change(sender, instance, created, **kwargs):
    if instance.attribute_type is not None:
        instance.attribute_type.calculate_total_resource()
        for quota_attribute_definition in instance.attribute_type.quota_attribute_definitions.all():
            for binding in quota_attribute_definition.quota_bindings.all():
                binding.update_consumed()

