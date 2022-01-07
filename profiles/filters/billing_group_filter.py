from django.forms import HiddenInput

from profiles.models import BillingGroup
from Squest.utils.squest_filter import SquestFilter


class BillingGroupFilter(SquestFilter):
    class Meta:
        model = BillingGroup
        fields = ['id', 'name']

    def __init__(self, *args, **kwargs):
        super(BillingGroupFilter, self).__init__(*args, **kwargs)
        self.filters['id'].field.widget = HiddenInput()
