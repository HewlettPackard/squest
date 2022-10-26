from resource_tracker.filters.tag_filter import TagFilterset
from resource_tracker.models import ResourceGroup


class ResourceGroupFilter(TagFilterset):
    class Meta:
        model = ResourceGroup
        fields = ['name', 'tag']
