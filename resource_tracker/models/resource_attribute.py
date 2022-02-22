from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from service_catalog import tasks


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


@receiver(pre_save, sender=ResourceAttribute)
def on_change(sender, instance, **kwargs):
    if instance.id:  # if edit
        old = ResourceAttribute.objects.get(id=instance.id)
        delta = instance.value - old.value
        # if value changed
        if instance.attribute_type is not None:
            instance.attribute_type.calculate_total_resource()
            if delta != 0:
                tasks.resource_attribute_update_consumed.delay(instance.id, delta)


@receiver(pre_delete, sender=ResourceAttribute)
def pre_delete(sender, instance, **kwargs):
    if instance.resource.billing_group and instance.attribute_type:
        instance.attribute_type.calculate_total_resource()
        delta = - instance.value
        tasks.resource_attribute_update_consumed.delay(instance.id, delta)
