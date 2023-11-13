from Squest.utils.squest_filter import SquestFilter
from resource_tracker_v2.models import AttributeDefinition


class AttributeDefinitionFilter(SquestFilter):
    class Meta:
        model = AttributeDefinition
        fields = ['name', 'attribute_group']
