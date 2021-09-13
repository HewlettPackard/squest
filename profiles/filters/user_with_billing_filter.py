import django_filters
from django import forms
from django.contrib.auth.models import User

from profiles.models import BillingGroup
from utils.squest_filter import SquestFilter


class BillingGroupFilter(django_filters.ModelMultipleChoiceFilter):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', BillingGroup.objects.filter())
        super().__init__(label='Billing groups', *args, **kwargs)


class UserBillingGroupsFilter(SquestFilter):
    billing_groups = BillingGroupFilter(widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                                                           'data-live-search': "true"}))

    no_billing_groups = django_filters.BooleanFilter(method='no_billing_group', label="No billing group",
                                                     widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'billing_groups']

    def no_billing_group(self, queryset, name, value):
        if not value:
            return queryset
        return User.objects.filter(billing_groups=None)
