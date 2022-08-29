from resource_tracker.models import ResourceGroupTextAttributeDefinition
from Squest.utils.squest_filter import SquestFilter


class ResourceGroupTextAttributeDefinitionFilter(SquestFilter):

    class Meta:
        model = ResourceGroupTextAttributeDefinition
        fields = '__all__'
