from Squest.utils.squest_filter import SquestFilter
from resource_tracker_v2.models import AttributeGroup


class AttributeGroupFilter(SquestFilter):
    class Meta:
        model = AttributeGroup
        fields = ['name']
