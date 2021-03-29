import django_filters

from service_catalog.models import Instance


class InstanceFilter(django_filters.FilterSet):
    state = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Instance
        fields = ['state']
