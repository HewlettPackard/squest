import django_filters
from django import forms

from resource_tracker.filters.tag_filter import TagFilter
from resource_tracker.models import ResourcePool
from Squest.utils.squest_filter import SquestFilter


class ResourcePoolFilter(SquestFilter):
    name = django_filters.CharFilter(widget=forms.TextInput(attrs={'class': 'form-control'}))
    tag = TagFilter(widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                                       'data-live-search': "true"}))

    class Meta:
        model = ResourcePool
        fields = ['name', 'tag']
