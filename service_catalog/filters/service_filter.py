from service_catalog.models import Service
from utils.squest_filter import SquestFilter


class ServiceFilter(SquestFilter):

    class Meta:
        model = Service
        fields = ['name']
