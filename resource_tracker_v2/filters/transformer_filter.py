from django.forms import SelectMultiple
from django_filters import MultipleChoiceFilter

from Squest.utils.squest_filter import SquestFilter
from resource_tracker_v2.models import Transformer, AttributeDefinition


class TransformerFilter(SquestFilter):

    class Meta:
        model = Transformer
        fields = ['attribute_definition']

    def __init__(self, *args, **kwargs):
        self.resource_group = kwargs.pop("resource_group", None)
        super(TransformerFilter, self).__init__(*args, **kwargs)
        self.filters['attribute_definition'].field.label = "Attribute"
        self.filters['attribute_definition'].field.choices = [(attribute_definition.id, attribute_definition.name) for attribute_definition in AttributeDefinition.objects.all()]
        if self.resource_group is not None:
            self.filters['attribute_definition'].field.choices = [(transformer.attribute_definition.id, transformer.attribute_definition.name) for transformer in self.resource_group.transformers.all()]

    attribute_definition = MultipleChoiceFilter(
        label="Attribute",
        choices=[],
        widget=SelectMultiple(attrs={'data-live-search': "true"}))
