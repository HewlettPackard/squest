from django.db import models
from taggit.managers import TaggableManager

from resource_tracker.models.resource_group_attribute_definition import ResourceGroupAttributeDefinition
from resource_tracker.models.exceptions import ExceptionResourceTracker
from resource_tracker.models.resource_group_text_attribute_definition import ResourceGroupTextAttributeDefinition


class ResourceGroup(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    tags = TaggableManager(related_name="resource_group_v1")

    def __str__(self):
        return self.name

    def add_attribute_definition(self, name, produce_for=None, consume_from=None, help_text=None):
        self.raise_if_attribute_name_exist(name)
        attribute = self.attribute_definitions.create(name=name, produce_for=produce_for, consume_from=consume_from,
                                                      help_text=help_text)
        attribute.save()
        self.init_attribute(attribute)
        return attribute

    def edit_attribute_definition(self, attribute_id, name, produce_for=None, consume_from=None, help_text=None):
        attribute = ResourceGroupAttributeDefinition.objects.get(id=attribute_id)
        if name != attribute.name:
            self.raise_if_attribute_name_exist(name)
        attribute.edit(name, produce_for, consume_from, help_text)
        self.init_attribute(attribute)
        return attribute

    def raise_if_attribute_name_exist(self, name):
        obj = ResourceGroupAttributeDefinition.objects.filter(name=name, resource_group=self)
        # if name is already used
        if len(obj) != 0:
            raise ExceptionResourceTracker.AttributeAlreadyExist(resource_group_name=self.name, attribute_name=name)

    def init_attribute(self, attribute):
        for resource in self.resources.all():
            resource.attributes.get_or_create(attribute_type=attribute)

    def add_text_attribute_definition(self, name, help_text=""):
        self.raise_if_text_attribute_name_exist(name)
        text_attribute = self.text_attribute_definitions.create(name=name, help_text=help_text)
        text_attribute.save()
        self.init_text_attribute(text_attribute)
        return text_attribute

    def edit_text_attribute_definition(self, attribute_id, name, help_text=""):
        text_attribute = ResourceGroupTextAttributeDefinition.objects.get(id=attribute_id)
        if name != text_attribute.name:
            self.raise_if_text_attribute_name_exist(name)
        text_attribute.edit(name, help_text)
        self.init_text_attribute(text_attribute)
        return text_attribute

    def raise_if_text_attribute_name_exist(self, name):
        obj = ResourceGroupTextAttributeDefinition.objects.filter(name=name, resource_group=self)
        # if name is already used
        if len(obj) != 0:
            raise ExceptionResourceTracker.AttributeAlreadyExist(resource_group_name=self.name, attribute_name=name)

    def init_text_attribute(self, attribute):
        for resource in self.resources.all():
            resource.text_attributes.get_or_create(text_attribute_type=attribute)

    def create_resource(self, name):
        resource, created = self.resources.get_or_create(name=name)
        if created:
            for attribute in self.attribute_definitions.all():
                resource.attributes.create(attribute_type=attribute)
            for attribute in self.text_attribute_definitions.all():
                resource.text_attributes.create(text_attribute_type=attribute)
        return resource

    def recalculate_total_resources(self):
        for attribute_definition in self.attribute_definitions:
            attribute_definition.calculate_total_resource()
