from resource_tracker.filters.tag_filter import TagFilterset
from resource_tracker.models import Resource


class ResourceFilter(TagFilterset):
    class Meta:
        model = Resource
        fields = ['name', 'tag']
