from django.forms import SelectMultiple

from resource_tracker.filters.tag_filter import TagFilter
from Squest.utils.squest_filter import SquestFilter


class GraphFilter(SquestFilter):
    tag = TagFilter(widget=SelectMultiple(attrs={'class': 'selectpicker',
                                                       'data-live-search': "true"}))

