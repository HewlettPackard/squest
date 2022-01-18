from django.db import models
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from taggit.managers import TaggableManager

from service_catalog.models.instance import Instance
from resource_tracker.models.resource_group import ResourceGroup


class Resource(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)
    resource_group = models.ForeignKey('ResourceGroup',
                                       on_delete=models.CASCADE,
                                       related_name='resources',
                                       related_query_name='resource',
                                       null=True)

    service_catalog_instance = models.ForeignKey(Instance,
                                                 on_delete=models.SET_NULL,
                                                 related_name='resources',
                                                 related_query_name='resource',
                                                 null=True)

    tags = TaggableManager()

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


@receiver(post_delete, sender=Resource)
def on_delete(sender, instance, **kwargs):
    """
    If a resource is deleted, the linked resource pool consumption is updated.
    """
    update_quota(instance.service_catalog_instance)
    if instance.resource_group_id:
        if ResourceGroup.objects.filter(id=instance.resource_group_id).exists():
            target_resource_group = ResourceGroup.objects.get(id=instance.resource_group_id)
            for resource_attribute in target_resource_group.attribute_definitions.all():
                resource_attribute.calculate_total_resource()


@receiver(pre_save, sender=Resource)
def pre_save(sender, instance, **kwargs):
    instance._old_instance = None
    instance._need_update = False
    if instance.id:
        old_instance = sender.objects.get(id=instance.id)
        if old_instance.service_catalog_instance != instance.service_catalog_instance:
            instance._old_instance = old_instance.service_catalog_instance
            instance._need_update = True


@receiver(post_save, sender=Resource)
def post_save(sender, instance, created, **kwargs):
    if created:
        update_quota(instance.service_catalog_instance)
    if instance._need_update:
        update_quota(instance._old_instance)
        update_quota(instance.service_catalog_instance)


def update_quota(instance):
    if instance:
        if instance.billing_group is not None:
            for binding in instance.billing_group.quota_bindings.all():
                binding.update_consumed()
