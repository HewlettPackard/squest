from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import Service


class ServiceFilter(SquestFilter):

    class Meta:
        model = Service
        fields = ['name', 'enabled']
