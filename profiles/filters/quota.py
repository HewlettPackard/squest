from Squest.utils.squest_filter import SquestFilter
from profiles.models import Quota


class QuotaFilter(SquestFilter):
    class Meta:
        model = Quota
        fields = ['scope', 'attribute_definition', 'attribute_definition__attribute_group']
