from Squest.utils.squest_filter import SquestFilter
from profiles.models import Quota


class QuotaFilter(SquestFilter):
    class Meta:
        model = Quota
        fields = ['scope', 'attribute_definition', 'attribute_definition__services']

    def __init__(self, *args, **kwargs):
        super(QuotaFilter, self).__init__(*args, **kwargs)
        self.filters['attribute_definition__services'].field.label = 'Services'
