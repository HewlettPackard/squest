from django_filters import CharFilter
from django import forms

from resource_tracker.filters.tag_filter import TagFilter
from resource_tracker.models import ResourceGroup
from utils.squest_filter import SquestFilter


class ResourceGroupFilter(SquestFilter):
    name = CharFilter(widget=forms.TextInput(attrs={'class': 'form-control'}))
    tag = TagFilter(widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                                       'data-live-search': "true"}))

    class Meta:
        model = ResourceGroup
        fields = ['name', 'tag']
