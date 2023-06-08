from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

from resource_tracker_v2.models import Transformer
from service_catalog.models.instance import Instance


class InvalidAttributeDefinition(Exception):
    pass


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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('resource_tracker:resource_group_resource_list', args=[self.resource_group.id])

    def set_attribute(self, attribute_definition, value):
        # check that the target attribute def is well declared as transformer
        if not self.resource_group.transformers.filter(attribute_definition=attribute_definition).exists():
            raise InvalidAttributeDefinition

        attribute, _ = self.resource_attributes.get_or_create(resource=self, attribute_definition=attribute_definition)
        attribute.value = value
        attribute.save()

        # notify transformer (we should have only one single transformer)
        transformer = Transformer.objects.get(attribute_definition=attribute_definition,
                                              resource_group=self.resource_group)
        transformer.calculate_total_produced()

    def get_attribute_value(self, attribute_definition):
        result = 0
        result += sum([item.value for item in self.resource_attributes.filter(resource=self,
                                                                              attribute_definition=attribute_definition)])
        return result

    def delete(self, using=None, keep_parents=False):
        transformers = self.resource_group.transformers.all()
        super(Resource, self).delete()
        for transformer in transformers:
            transformer.calculate_total_produced()
            transformer.notify_parent()

    def delete_attribute_from_def(self, attribute_definition):
        for attribute in self.resource_attributes.all():
            if attribute.attribute_definition == attribute_definition:
                attribute.delete()
