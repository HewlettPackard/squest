from django.forms import SelectMultiple, CheckboxInput
from django.utils import timezone
from django_filters import MultipleChoiceFilter, BooleanFilter
from service_catalog.models import Announcement, BootstrapType
from Squest.utils.squest_filter import SquestFilter


class AnnouncementFilter(SquestFilter):
    class Meta:
        model = Announcement
        fields = ['title', 'created_by__username', 'type']

    def __init__(self, *args, **kwargs):
        super(AnnouncementFilter, self).__init__(*args, **kwargs)
        self.filters['created_by__username'].field.label = "Owner"

    type = MultipleChoiceFilter(
        choices=BootstrapType.choices,
        widget=SelectMultiple(attrs={'data-live-search': "true"})
    )
    opens = BooleanFilter(
        label='Active only',
        method='get_active_announcements',
        widget=CheckboxInput(attrs={'class': 'form-control-checkbox'})
    )

    def get_active_announcements(self, queryset, field_name, value):
        if value:
            now = timezone.now()
            return queryset.filter(date_start__lte=now, date_stop__gte=now)
        return queryset
