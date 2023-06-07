from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager


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

    def get_absolute_url(self):
        return reverse("resource_tracker:resource_group_list")
