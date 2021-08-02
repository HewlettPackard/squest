import django_filters
from django import forms

from service_catalog.models import Support


class SupportFilter(django_filters.FilterSet):
    OPENED = 'opened'
    CLOSED = 'closed'
    CHOICES = (
        (OPENED, 'OPENED'),
        (CLOSED, 'CLOSED'),
    )
    state = django_filters.MultipleChoiceFilter(
        choices=CHOICES,
        null_value=None,
        widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                           'data-live-search': "true"}))

    instance = django_filters.CharFilter(field_name='instance__name',
                                         lookup_expr='exact',
                                         widget=forms.TextInput(attrs={'class': 'form-control'}))

    instance_id = django_filters.CharFilter(field_name='instance__id',
                                            lookup_expr='exact',
                                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Support
        fields = ['instance', 'instance_id', 'state']
