from profiles.models import BillingGroup
from Squest.utils.squest_filter import SquestFilter


class BillingGroupFilter(SquestFilter):
    class Meta:
        model = BillingGroup
        fields = ['name']
