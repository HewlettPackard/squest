from django.forms import SelectMultiple
from django_filters import MultipleChoiceFilter
from service_catalog.models import Instance, Service
from service_catalog.models.instance import InstanceState
from utils.squest_filter import SquestFilter


class InstanceFilter(SquestFilter):
    class Meta:
        model = Instance
        fields = ['name', 'service__id', 'state']

    state = MultipleChoiceFilter(
        choices=InstanceState.choices,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    service__id = MultipleChoiceFilter(
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    def __init__(self, *args, **kwargs):
        super(InstanceFilter, self).__init__(*args, **kwargs)
        self.filters['service__id'].field.label = 'Type'
        self.filters['service__id'].field.choices = [(service.id, service.name) for service in Service.objects.all()]
