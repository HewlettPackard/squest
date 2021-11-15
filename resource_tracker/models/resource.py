from django.db import models
from taggit.managers import TaggableManager

from service_catalog.models import Instance


class Resource(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)
    resource_group = models.ForeignKey('ResourceGroup',
                                       on_delete=models.SET_NULL,
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
