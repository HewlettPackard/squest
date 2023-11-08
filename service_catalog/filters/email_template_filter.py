from django.forms import SelectMultiple
from django_filters import MultipleChoiceFilter

from Squest.utils.squest_filter import SquestFilter
from service_catalog.models import EmailTemplate


class EmailTemplateFilter(SquestFilter):
    class Meta:
        model = EmailTemplate
        fields = ['name']
