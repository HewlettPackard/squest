from resource_tracker_v2.filters.tag_filter import TagFilterset
from resource_tracker_v2.models import ResourceGroup


class ResourceGroupFilter(TagFilterset):
    class Meta:
        model = ResourceGroup
        fields = ['name', 'tag']
