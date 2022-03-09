from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from taggit.managers import TaggableManager

from service_catalog import tasks
from service_catalog.models.instance import Instance


class Resource(models.Model):
    name = models.CharField(max_length=100,
                            blank=False)
    resource_group = models.ForeignKey('ResourceGroup',
                                       on_delete=models.CASCADE,
                                       related_name='resources',
                                       related_query_name='resource')

    service_catalog_instance = models.ForeignKey(Instance,
                                                 on_delete=models.SET_NULL,
                                                 related_name='resources',
                                                 related_query_name='resource',
                                                 null=True,
                                                 blank=True)

    tags = TaggableManager()

    is_deleted_on_instance_deletion = models.BooleanField(default=True,
                                                          verbose_name="Delete this resource on instance deletion")

    class Meta:
        unique_together = ('name', 'resource_group')

    @property
    def billing_group(self):
        if self.service_catalog_instance:
            if self.service_catalog_instance.billing_group:
                return self.service_catalog_instance.billing_group
        return None

    def __str__(self):
        return self.name

    def set_attribute(self, attribute_type, value):
        attribute, _ = self.attributes.get_or_create(attribute_type=attribute_type)
        attribute.value = value
        attribute.save()

    def set_text_attribute(self, text_attribute_type, value):
        text_attribute, _ = self.text_attributes.get_or_create(text_attribute_type=text_attribute_type)
        text_attribute.value = value
        text_attribute.save()


@receiver(pre_save, sender=Resource)
def pre_save(sender, instance, **kwargs):
    instance._old_billing = None
    instance._need_update = False
    if instance.id:
        old_instance = sender.objects.get(id=instance.id)
        if old_instance.service_catalog_instance != instance.service_catalog_instance:
            instance._need_update = True
            if old_instance.service_catalog_instance:
                instance._old_billing = old_instance.service_catalog_instance.billing_group


@receiver(post_save, sender=Resource)
def post_save(sender, instance, created, **kwargs):
    if created:
        if instance.billing_group:
            tasks.async_quota_bindings_add_resource.delay(resource_id=instance.id, billing_id=instance.billing_group.id)
    if instance._need_update:
        if instance.billing_group:
            tasks.async_quota_bindings_add_resource.delay(resource_id=instance.id, billing_id=instance.billing_group.id)
        if instance._old_billing:
            tasks.async_quota_bindings_remove_resource.delay(resource_id=instance.id,
                                                             billing_id=instance._old_billing.id)
