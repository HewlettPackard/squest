from django.forms import SelectMultiple
from django_filters import MultipleChoiceFilter

from Squest.utils.squest_filter import SquestFilter
from resource_tracker_v2.models import Transformer


class TransformerFilter(SquestFilter):

    class Meta:
        model = Transformer
        fields = ['attribute_definition']

    def __init__(self, *args, **kwargs):
        super(TransformerFilter, self).__init__(*args, **kwargs)
        self.filters['attribute_definition'].field.label = "Attribute"
        from resource_tracker_v2.models import AttributeDefinition
        # TODO: filter to have only linked attributes. Here the list contains all attributes
        self.filters['attribute_definition'].field.choices = [(attribute.id, attribute.name) for attribute in AttributeDefinition.objects.all()]

    attribute_definition = MultipleChoiceFilter(
        label="Service",
        choices=[],
        widget=SelectMultiple(attrs={'data-live-search': "true"}))
