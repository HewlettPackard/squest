from django.db.models import CharField
from django.urls import reverse
from taggit.managers import TaggableManager

from Squest.utils.squest_model import SquestModel


class ResourceGroup(SquestModel):

    name = CharField(max_length=100,
                     blank=False,
                     unique=True)

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def create_resource(self, name):
        resource, _ = self.resources.get_or_create(name=name, resource_group=self)
        return resource

    def get_absolute_url(self):
        return reverse("resource_tracker_v2:resourcegroup_details",args=[self.pk])
