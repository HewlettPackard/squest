from django.contrib.auth.models import User
from django.forms import HiddenInput, CheckboxInput
from django_filters import MultipleChoiceFilter, BooleanFilter
from service_catalog.models import Instance, Service
from service_catalog.models.instance import InstanceState
from Squest.utils.squest_filter import SquestFilter


class InstanceFilter(SquestFilter):
    class Meta:
        model = Instance
        fields = ['name', 'id', 'spoc', 'service', 'state', 'billing_group']
    spoc = MultipleChoiceFilter()
    state = MultipleChoiceFilter(choices=InstanceState.choices)
    service = MultipleChoiceFilter()

    no_billing_groups = BooleanFilter(method='no_billing_group', label="No billing group", widget=CheckboxInput())
    no_spocs = BooleanFilter(method='no_spoc', label="No SPOC", widget=CheckboxInput())

    def __init__(self, *args, **kwargs):
        super(InstanceFilter, self).__init__(*args, **kwargs)
        self.filters['id'].field.widget = HiddenInput()
        self.filters['service'].field.choices = [(service.id, service.name) for service in Service.objects.all()]
        self.filters['spoc'].field.choices = [(spoc.id, spoc.username) for spoc in User.objects.all()]

    def no_billing_group(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(billing_group=None)

    def no_spoc(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(spoc=None)