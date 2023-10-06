from resource_tracker_v2.filters.tag_filter import TagFilterset
from resource_tracker_v2.models import Resource


class ResourceFilter(TagFilterset):
    class Meta:
        model = Resource
        fields = ['resource_group','service_catalog_instance', 'name', 'tag']
