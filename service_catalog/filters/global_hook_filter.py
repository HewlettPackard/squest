from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import InstanceHook, RequestHook


class InstanceHookFilter(SquestFilter):
    class Meta:
        model = InstanceHook
        fields = ['name', 'state', 'services']


class RequestHookFilter(SquestFilter):
    class Meta:
        model = RequestHook
        fields = ['name', 'state', 'operations']
