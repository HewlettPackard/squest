from django.db import models


class ResourceTextAttribute(models.Model):
    value = models.CharField(max_length=500, default='')

    resource = models.ForeignKey('Resource',
                                 on_delete=models.CASCADE,
                                 related_name='text_attributes',
                                 related_query_name='text_attribute',
                                 null=True)

    text_attribute_type = models.ForeignKey('ResourceGroupTextAttributeDefinition',
                                            on_delete=models.CASCADE,
                                            related_name='text_attribute_types',
                                            related_query_name='text_attribute_type',
                                            default=""
                                            )

    def __str__(self):
        return str(self.value)
