from django.contrib.auth.models import User
from django.forms import SelectMultiple, HiddenInput
from django_filters import MultipleChoiceFilter

from service_catalog.models import Request
from service_catalog.models.operations import OperationType
from service_catalog.models.request import RequestState
from Squest.utils.squest_filter import SquestFilter


class RequestFilter(SquestFilter):
    class Meta:
        model = Request
        fields = ['instance__name', 'instance__id', 'user__id', 'instance__service__id', 'operation', 'operation__type',
                  'state']



    instance__service__id = MultipleChoiceFilter(
        label="Service",
        choices=[],
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    operation__type = MultipleChoiceFilter(
        label="Type",
        choices=OperationType.choices,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    operation = MultipleChoiceFilter(
        label="Operation",
        choices=[],
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    state = MultipleChoiceFilter(
        choices=[state for state in RequestState.choices if state[0] != RequestState.ARCHIVED],
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    user__id = MultipleChoiceFilter()

    def __init__(self, *args, **kwargs):
        super(RequestFilter, self).__init__(*args, **kwargs)
        self.filters['instance__name'].field.label = 'Instance'
        self.filters['instance__id'].field.widget = HiddenInput()
        self.filters['user__id'].field.label = 'User'
        self.filters['user__id'].field.choices = [(requester.id, requester.username) for requester in
                                                  User.objects.all().order_by("username")]
        from service_catalog.models import Service
        from service_catalog.models.operations import Operation
        self.filters['instance__service__id'].field.choices = [(service.id, service.name) for service in Service.objects.all().order_by("name")]
        self.filters['operation'].field.choices = [(operation.id, f"{operation.service.name}-{operation.name}") for operation in Operation.objects.all().order_by("service__name", "name")]

    @property
    def qs(self):
        return super().qs.exclude(state=RequestState.ARCHIVED)


class RequestArchivedFilter(SquestFilter):
    class Meta:
        model = Request
        fields = ['instance__name', 'instance__id', 'user__username', 'instance__service__name', 'operation__name', 'operation__type']

    operation__type = MultipleChoiceFilter(
        choices=OperationType.choices,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    def __init__(self, *args, **kwargs):
        super(RequestArchivedFilter, self).__init__(*args, **kwargs)
        self.filters['instance__name'].field.label = 'Instance'
        self.filters['instance__id'].field.widget = HiddenInput()
        self.filters['user__username'].field.label = 'User'
        self.filters['instance__service__name'].field.label = 'Service name'
        self.filters['operation__name'].field.label = 'Operation name'
        self.filters['operation__type'].field.label = 'Type'

    @property
    def qs(self):
        return super().qs.filter(state=RequestState.ARCHIVED)
