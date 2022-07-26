from django.forms import SelectMultiple
from django_filters import MultipleChoiceFilter

from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import CustomLink, Service


class CustomLinkFilter(SquestFilter):
    class Meta:
        model = CustomLink
        fields = ['name', 'services']

    def __init__(self, *args, **kwargs):
        super(CustomLinkFilter, self).__init__(*args, **kwargs)
        from service_catalog.models import Service
        self.filters['services'].field.choices = [(service.id, service.name) for service in Service.objects.all()]

    services = MultipleChoiceFilter(
        label="Service",
        choices=[],
        widget=SelectMultiple(attrs={'data-live-search': "true"}))
