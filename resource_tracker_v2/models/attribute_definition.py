from django.db.models import CharField, ForeignKey, CASCADE
from django.urls import reverse

from Squest.utils.squest_model import SquestModel
from resource_tracker_v2.models.attribute_group import AttributeGroup


class AttributeDefinition(SquestModel):
    name = CharField(max_length=100,
                     unique=True,
                     blank=False)

    description = CharField(max_length=100, default='', null=True, blank=True)

    attribute_group = ForeignKey(
        AttributeGroup,
        blank=True,
        null=True,
        on_delete=CASCADE,
        related_name="attribute_definitions",
        related_query_name="attribute_definition"
    )

    def delete(self, using=None, keep_parents=False):
        # remove the pointer to this attribute in all transformer that were using it
        from resource_tracker_v2.models import Transformer
        for transformer in Transformer.objects.filter(consume_from_attribute_definition=self):
            transformer.consume_from_resource_group = None
            transformer.consume_from_attribute_definition = None
            transformer.save()

        super(AttributeDefinition, self).delete()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("resource_tracker_v2:attributedefinition_details", args=[self.pk])
