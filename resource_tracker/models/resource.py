from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from taggit.managers import TaggableManager

from service_catalog.models import Instance


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
        return f"{self.name}[" + ",".join([f"{attribute.attribute_type.name}: {attribute.value}"
                                           for attribute in self.attributes.all()]) + "]"

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
    if instance.resource_group_id:
        from resource_tracker.models import ResourceGroup
        if ResourceGroup.objects.filter(id=instance.resource_group_id).exists():
            target_resource_group = ResourceGroup.objects.get(id=instance.resource_group_id)
            for resource_attribute in target_resource_group.attribute_definitions.all():
                resource_attribute.calculate_total_resource()
