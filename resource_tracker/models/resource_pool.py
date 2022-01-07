from django.db import models
from taggit.managers import TaggableManager


class ResourcePool(models.Model):
    name = models.CharField(max_length=100,
                            blank=False,
                            unique=True)

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def add_attribute_definition(self, name, over_commitment_producers=1, over_commitment_consumers=1):
        return self.attribute_definitions.create(name=name,
                                                 over_commitment_producers=over_commitment_producers,
                                                 over_commitment_consumers=over_commitment_consumers)

    def update_all_consumed_and_produced(self):
        for attribute in self.attribute_definitions.all():
            attribute.calculate_total_consumed()
            attribute.calculate_total_produced()
