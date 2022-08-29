from resource_tracker.models import ResourceGroupAttributeDefinition
from Squest.utils.squest_filter import SquestFilter


class ResourceGroupAttributeDefinitionFilter(SquestFilter):

    class Meta:
        model = ResourceGroupAttributeDefinition
        fields = '__all__'
