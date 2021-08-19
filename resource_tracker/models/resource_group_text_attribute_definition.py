from django.db import models


class ResourceGroupTextAttributeDefinition(models.Model):
    class Meta:
        unique_together = ('name', 'resource_group_definition',)

    name = models.CharField(max_length=100,
                            blank=False)
    resource_group_definition = models.ForeignKey('ResourceGroup',
                                                  on_delete=models.PROTECT,
                                                  related_name='text_attribute_definitions',
                                                  related_query_name='text_attribute_definition',
                                                  null=True)

    help_text = models.CharField(max_length=100, default='', null=True, blank=True)

    def edit(self, name, help_text):
        self.name = name
        self.help_text = help_text
        self.save()

    def __str__(self):
        return f"{self.resource_group_definition} - {self.name}"
