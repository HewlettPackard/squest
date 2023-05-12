from django.db import models
from taggit.managers import TaggableManager

from resource_tracker_v2.models.resource_attribute import ResourceAttribute


class ResourceGroup(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def create_resource(self, name):
        resource, _ = self.resources.get_or_create(name=name, resource_group=self)
        return resource
