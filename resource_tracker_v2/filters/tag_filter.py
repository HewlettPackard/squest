from django_filters import ModelMultipleChoiceFilter, ChoiceFilter
from taggit.models import Tag

from Squest.utils.squest_filter import SquestFilter

map_filter_type = {
    "OR": False,
    "AND": True
}


class TagFilter(ModelMultipleChoiceFilter):
    """
    Match on one or more assigned tags. If multiple tags are specified (e.g. ?tag=foo&tag=bar),
    the queryset is filtered
    to objects matching all tags.
    """

    def __init__(self, *args, **kwargs):
        # we only show tags that are used on object
        used_tags = Tag.objects.exclude(taggit_taggeditem_items__object_id__isnull=True)

        kwargs.setdefault('field_name', 'tags__name')
        kwargs.setdefault('to_field_name', 'name')
        kwargs.setdefault('conjoined', False)
        kwargs.setdefault('queryset', used_tags)

        super().__init__(label='Tags in', *args, **kwargs)


class TagFilterset(SquestFilter):
    tag = TagFilter()
    tag_filter_type = ChoiceFilter(method='fake_filter_method', label="Tags filter method:",
                                   choices=[("AND", "AND")], required=False, empty_label="OR")

    def is_valid(self):
        if hasattr(self, 'data'):
            conjoined = self.data.get('tag_filter_type', "OR") or "OR"
            self.filters['tag'].conjoined = map_filter_type[conjoined]
            self.base_filters['tag'].conjoined = conjoined
        return super(TagFilterset, self).is_valid()
