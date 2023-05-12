from django.db import models


class ResourceAttribute(models.Model):
    value = models.PositiveIntegerField(default=0)

    resource = models.ForeignKey('Resource',
                                 on_delete=models.CASCADE,
                                 related_name='resource_attributes',
                                 related_query_name='resource_attribute',
                                 null=True)

    attribute_definition = models.ForeignKey('AttributeDefinition',
                                             on_delete=models.CASCADE,
                                             related_name='resource_attributes',
                                             related_query_name='resource_attribute',
                                             null=True)

    def __str__(self):
        return str(self.value)
