from profiles.models import Quota
from Squest.utils.squest_filter import SquestFilter


class QuotaFilter(SquestFilter):
    class Meta:
        model = Quota
        fields = ['name']
