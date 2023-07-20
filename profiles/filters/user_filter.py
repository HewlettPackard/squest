import django_filters
from django import forms
from django.contrib.auth.models import User

from Squest.utils.squest_filter import SquestFilter


class UserFilter(SquestFilter):
    class Meta:
        model = User
        fields = ['username', 'email']

    no_organization = django_filters.BooleanFilter(method='has_no_organization',
                                                   label="No organization",
                                                   widget=forms.CheckboxInput(attrs={'class': 'form-control-checkbox'}))

    def has_no_organization(self, queryset, field_name, value):
        if not value:
            return queryset
        return queryset.filter(groups__isnull=True)
