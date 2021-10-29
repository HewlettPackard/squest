import django_filters
from taggit.models import Tag


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
