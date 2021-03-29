import django_filters

from service_catalog.models import Request


class RequestFilter(django_filters.FilterSet):
    state = django_filters.CharFilter(lookup_expr='iexact')
    instance = django_filters.CharFilter(field_name='instance', lookup_expr='name')

    class Meta:
        model = Request
        fields = ['state', 'instance']
