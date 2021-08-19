from django.db import models
from taggit.managers import TaggableManager


class ResourcePool(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def add_attribute_definition(self, name):
        return self.attribute_definitions.create(name=name)
