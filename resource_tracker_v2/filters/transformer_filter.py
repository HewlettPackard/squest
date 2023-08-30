from Squest.utils.squest_filter import SquestFilter
from resource_tracker_v2.models import Transformer


class TransformerFilter(SquestFilter):

    class Meta:
        model = Transformer
        fields = ['resource_group', 'attribute_definition']
