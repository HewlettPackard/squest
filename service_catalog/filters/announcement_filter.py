from django.forms import SelectMultiple, Form
from django.utils import timezone
from django_filters import DateTimeFilter, MultipleChoiceFilter
from tempus_dominus.widgets import DateTimePicker

from service_catalog.models import Announcement, BootstrapType
from utils.squest_filter import SquestFilter


class AnnouncementFilterForm(Form):
    def clean(self):
        cleaned_data = super(AnnouncementFilterForm, self).clean()
        start = cleaned_data.get("start")
        stop = cleaned_data.get("stop")
        if start and stop:
            if start > stop:
                self._errors['start'] = self._errors.get('start', [])
                self._errors['start'].append("Start date must be before end date.")
        return cleaned_data


class AnnouncementFilter(SquestFilter):
    class Meta:
        model = Announcement
        fields = ['title', 'created_by__username', 'type']
        form = AnnouncementFilterForm

    def __init__(self, *args, **kwargs):
        super(AnnouncementFilter, self).__init__(*args, **kwargs)
        self.filters['created_by__username'].field.label = "Owner"
        self.filters['stop'].field.widget = DateTimePicker(
            options={
                'timeZone': str(timezone.get_current_timezone()),
                'icons': {
                    'time': 'fa fa-clock',
                }
            }, attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
        self.filters['start'].field.widget = DateTimePicker(
            options={
                'timeZone': str(timezone.get_current_timezone()),
                'icons': {
                    'time': 'fa fa-clock',
                }
            }, attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )

    start = DateTimeFilter(label="Start", method='get_start')
    stop = DateTimeFilter(label="Stop", method='get_stop')
    type = MultipleChoiceFilter(
        choices=BootstrapType.choices,
        widget=SelectMultiple(attrs={'data-live-search': "true"}))

    def get_start(self, queryset, field_name, value):
        return queryset.filter(date_start__gte=value)

    def get_stop(self, queryset, field_name, value):
        return queryset.filter(date_stop__lte=value)
