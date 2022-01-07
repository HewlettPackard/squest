from django.forms import SelectMultiple, HiddenInput, CheckboxInput
from django_filters import MultipleChoiceFilter, BooleanFilter
from service_catalog.models import Instance, Service
from service_catalog.models.instance import InstanceState
from Squest.utils.squest_filter import SquestFilter


class InstanceFilter(SquestFilter):
    class Meta:
        model = Instance
        fields = ['name', 'id', 'spoc__username', 'service__id', 'state', 'billing_group']

    state = MultipleChoiceFilter(
        choices=InstanceState.choices,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    service__id = MultipleChoiceFilter(
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    no_billing_groups = BooleanFilter(method='no_billing_group', label="No billing group", widget=CheckboxInput())

    def __init__(self, *args, **kwargs):
        super(InstanceFilter, self).__init__(*args, **kwargs)
        self.filters['spoc__username'].field.label = 'SPOC (Name)'
        self.filters['service__id'].field.label = 'Type'
        self.filters['id'].field.widget = HiddenInput()
        self.filters['service__id'].field.choices = [(service.id, service.name) for service in Service.objects.all()]

    def no_billing_group(self, queryset, name, value):
        if not value:
            return queryset
        return Instance.objects.filter(billing_group=None)
