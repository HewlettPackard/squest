from profiles.models import BillingGroup
from utils.squest_filter import SquestFilter


class BillingGroupFilter(SquestFilter):
    class Meta:
        model = BillingGroup
        fields = ['name']
