from django.forms import SelectMultiple
from django_filters import MultipleChoiceFilter

from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import GlobalHook
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState
from service_catalog.models.state_hooks import HookModel


class GlobalHookFilter(SquestFilter):
    class Meta:
        model = GlobalHook
        fields = ['name', 'model']

    model = MultipleChoiceFilter(
        choices=HookModel.choices,
        widget=SelectMultiple())

    state_instance = MultipleChoiceFilter(
        label="Instance state",
        method='add_states_in_filter',
        choices=InstanceState.choices,
        null_value=None,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    state_request = MultipleChoiceFilter(
        label="Request state",
        method='add_states_in_filter',
        choices=RequestState.choices,
        null_value=None,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    def __init__(self, *args, **kwargs):
        super(GlobalHookFilter, self).__init__(*args, **kwargs)
        self.state_filter_value = list()

    def add_states_in_filter(self, queryset, field_name, value):
        self.state_filter_value += value
        return queryset

    def filter_queryset(self, queryset):
        queryset = super(GlobalHookFilter, self).filter_queryset(queryset)
        tmp = self.state_filter_value
        self.state_filter_value = []
        return queryset.filter(state__in=tmp)
