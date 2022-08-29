from resource_tracker.models import ResourcePoolAttributeDefinition
from Squest.utils.squest_filter import SquestFilter


class ResourcePoolAttributeDefinitionFilter(SquestFilter):

    class Meta:
        model = ResourcePoolAttributeDefinition
        fields = '__all__'
