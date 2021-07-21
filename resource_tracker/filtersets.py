import django_filters
from django import forms
from taggit.models import Tag

from resource_tracker.models import ResourcePool


class TagFilter(django_filters.ModelMultipleChoiceFilter):
    """
    Match on one or more assigned tags. If multiple tags are specified (e.g. ?tag=foo&tag=bar),
    the queryset is filtered
    to objects matching all tags.
    """

    def __init__(self, *args, **kwargs):

        kwargs.setdefault('field_name', 'tags__slug')
        kwargs.setdefault('to_field_name', 'slug')
        kwargs.setdefault('conjoined', False)
        kwargs.setdefault('queryset', Tag.objects.all())

        super().__init__(label='Tags', *args, **kwargs)


class ResourcePoolFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(widget=forms.TextInput(attrs={'class': 'form-control'}))
    tag = TagFilter(widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    class Meta:
        model = ResourcePool
        fields = ['name', 'tag']
