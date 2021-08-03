import django_filters
from django import forms
from django.contrib.auth.models import User
from taggit.models import Tag

from profiles.models import BillingGroup
from resource_tracker.models import ResourcePool, ResourceGroup


class BillingGroupFilter(django_filters.ModelMultipleChoiceFilter):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', BillingGroup.objects.filter())
        super().__init__(label='Billing groups', *args, **kwargs)


class TagFilter(django_filters.ModelMultipleChoiceFilter):
    """
    Match on one or more assigned tags. If multiple tags are specified (e.g. ?tag=foo&tag=bar),
    the queryset is filtered
    to objects matching all tags.
    """

    def __init__(self, *args, **kwargs):
        # we only show tags that are used on object
        used_tags = Tag.objects.exclude(taggit_taggeditem_items__object_id__isnull=True)

        kwargs.setdefault('field_name', 'tags__slug')
        kwargs.setdefault('to_field_name', 'slug')
        kwargs.setdefault('conjoined', True)
        kwargs.setdefault('queryset', used_tags)

        super().__init__(label='Tags in', *args, **kwargs)


class ResourcePoolFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(widget=forms.TextInput(attrs={'class': 'form-control'}))
    tag = TagFilter(widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                                       'data-live-search': "true"}))

    class Meta:
        model = ResourcePool
        fields = ['name', 'tag']


class ResourceGroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(widget=forms.TextInput(attrs={'class': 'form-control'}))
    tag = TagFilter(widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                                       'data-live-search': "true"}))

    class Meta:
        model = ResourceGroup
        fields = ['name', 'tag']


class GraphFilter(django_filters.FilterSet):
    tag = TagFilter(widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                                       'data-live-search': "true"}))


class UserFilter(django_filters.FilterSet):

    billing_groups = BillingGroupFilter(widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                                                           'data-live-search': "true"}))

    no_billing_groups = django_filters.BooleanFilter(method='no_billing_group', label="No billing group",
                                                     widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['billing_groups']

    def no_billing_group(self, queryset, name, value):
        if not value:
            return queryset
        return User.objects.filter(billing_groups=None)
