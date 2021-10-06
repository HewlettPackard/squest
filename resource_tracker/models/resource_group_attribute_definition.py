from django.db import models

from resource_tracker.models import ResourceAttribute


class ResourceGroupAttributeDefinition(models.Model):
    name = models.CharField(max_length=100,
                            blank=False)
    resource_group_definition = models.ForeignKey('ResourceGroup',
                                                  on_delete=models.CASCADE,
                                                  related_name='attribute_definitions',
                                                  related_query_name='attribute_definition',
                                                  null=True)
    consume_from = models.ForeignKey('ResourcePoolAttributeDefinition',
                                     on_delete=models.SET_NULL,
                                     related_name='consumers',
                                     related_query_name='consumer',
                                     null=True)
    produce_for = models.ForeignKey('ResourcePoolAttributeDefinition',
                                    on_delete=models.SET_NULL,
                                    related_name='producers',
                                    related_query_name='producer',
                                    null=True)

    help_text = models.CharField(max_length=100, default='', null=True, blank=True)

    def __str__(self):
        return f"{self.resource_group_definition} - {self.name}"

    def get_total_resource(self):
        total = 0
        for resource in self.resource_group_definition.resources.all():
            try:
                total += resource.attributes.get(attribute_type=self).value
            except ResourceAttribute.DoesNotExist:
                pass
        return total

    def edit(self, name, produce_for, consume_from, help_text):
        self.name = name
        self.consume_from = consume_from
        self.produce_for = produce_for
        self.help_text = help_text
        self.save()

    class Meta:
        unique_together = ('name', 'resource_group_definition',)
