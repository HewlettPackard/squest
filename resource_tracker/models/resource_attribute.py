from django.db import models
from django.db.models.signals import pre_save, pre_delete, post_save
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

    def quota_bindings_update_consumed(self, delta):
        if self.resource.billing_group:
            for quota in self.attribute_type.quota.all():
                for binding in quota.quota_bindings.filter(
                        billing_group=self.resource.billing_group):
                    binding.calculate_consumed(delta)


@receiver(pre_save, sender=ResourceAttribute)
def on_change(sender, instance, **kwargs):
    if instance.id:  # if edit
        old = ResourceAttribute.objects.get(id=instance.id)
        delta = instance.value - old.value
        # if value changed
        if instance.attribute_type is not None:
            if delta != 0:
                instance.attribute_type.calculate_resource(delta)
                tasks.async_resource_attribute_quota_bindings_update_consumed.delay(instance.id, delta)


@receiver(post_save, sender=ResourceAttribute)
def on_create(sender, instance, created, **kwargs):
    if created and instance.value:
        instance.attribute_type.calculate_resource(instance.value)
        tasks.async_resource_attribute_quota_bindings_update_consumed.delay(instance.id, instance.value)


@receiver(pre_delete, sender=ResourceAttribute)
def pre_delete(sender, instance, **kwargs):
    delta = - instance.value
    if instance.attribute_type:
        instance.attribute_type.calculate_resource(delta)
        if instance.resource.billing_group:
            tasks.async_resource_attribute_quota_bindings_update_consumed.delay(instance.id, delta)
