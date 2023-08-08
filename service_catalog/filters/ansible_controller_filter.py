from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import AnsibleController


class AnsibleControllerFilter(SquestFilter):
    class Meta:
        model = AnsibleController
        fields = ['name', 'host']
