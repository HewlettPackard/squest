from django import forms

from resource_tracker.filters.tag_filter import TagFilter
from resource_tracker.models import Resource
from utils.squest_filter import SquestFilter


class ResourceFilter(SquestFilter):
    tag = TagFilter(widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                                       'data-live-search': "true"}))

    class Meta:
        model = Resource
        fields = ['name', 'tag']
