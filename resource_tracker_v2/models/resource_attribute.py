from django.db.models import PositiveIntegerField, ForeignKey, CASCADE

from Squest.utils.squest_model import SquestModel


class ResourceAttribute(SquestModel):
    value = PositiveIntegerField(default=0)

    resource = ForeignKey('Resource',
                          on_delete=CASCADE,
                          related_name='resource_attributes',
                          related_query_name='resource_attribute',
                          null=True)

    attribute_definition = ForeignKey('AttributeDefinition',
                                      on_delete=CASCADE,
                                      related_name='resource_attributes',
                                      related_query_name='resource_attribute',
                                      null=True)

    def __str__(self):
        return str(self.value)
