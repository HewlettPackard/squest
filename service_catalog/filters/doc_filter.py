from django.forms import SelectMultiple
from django_filters import ModelMultipleChoiceFilter

from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import Doc, Service


class ServiceFilter(ModelMultipleChoiceFilter):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Service.objects.filter())
        super().__init__(label='Services', *args, **kwargs)


class DocFilter(SquestFilter):
    services = ServiceFilter(widget=SelectMultiple(attrs={'data-live-search': "true"}))

    class Meta:
        model = Doc
        fields = ['title', 'services']
