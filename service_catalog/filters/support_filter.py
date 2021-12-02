from django.forms import SelectMultiple, HiddenInput
from django_filters import MultipleChoiceFilter
from service_catalog.models import Support
from service_catalog.models.support import SupportState
from Squest.utils.squest_filter import SquestFilter


class SupportFilter(SquestFilter):
    class Meta:
        model = Support
        fields = ['title', 'instance__id', 'instance__name', 'user_open__username', 'state']

    state = MultipleChoiceFilter(
        choices=SupportState.choices,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    def __init__(self, *args, **kwargs):
        super(SupportFilter, self).__init__(*args, **kwargs)
        self.filters['instance__name'].field.label = "Instance"
        self.filters['instance__id'].field.widget = HiddenInput()
        self.filters['user_open__username'].field.label = "User open"
