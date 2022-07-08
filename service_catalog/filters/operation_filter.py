from django.forms import SelectMultiple
from django_filters import MultipleChoiceFilter
from service_catalog.models import Operation
from service_catalog.models.operations import OperationType
from Squest.utils.squest_filter import SquestFilter


class OperationFilter(SquestFilter):
    class Meta:
        model = Operation
        fields = ['name', 'type', 'job_template__name', 'auto_accept', 'auto_process', 'process_timeout_second']

    type = MultipleChoiceFilter(
        choices=OperationType.choices,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))


class OperationFilterLimited(SquestFilter):
    class Meta:
        model = Operation
        fields = ['name']
