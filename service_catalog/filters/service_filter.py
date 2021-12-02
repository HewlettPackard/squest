from service_catalog.models import Service
from Squest.utils.squest_filter import SquestFilter


class ServiceFilter(SquestFilter):

    class Meta:
        model = Service
        fields = ['name', 'enabled']
