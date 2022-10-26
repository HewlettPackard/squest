from resource_tracker.filters.tag_filter import TagFilterset
from resource_tracker.models import ResourcePool


class ResourcePoolFilter(TagFilterset):
    class Meta:
        model = ResourcePool
        fields = ['name', 'tag']
