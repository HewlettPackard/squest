from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone
from tempus_dominus.widgets import DateTimePicker

from service_catalog.models.announcement import Announcement, AnnouncementType


class AnnouncementForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields['date_start'].widget = DateTimePicker(
            options={
                'useCurrent': True,
                'timeZone': str(timezone.get_current_timezone()),
                'collapse': False,
                'minDate': str(timezone.now().astimezone().strftime("%Y-%m-%d 00:00:00")),
            }, attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
        self.fields['date_stop'].widget = DateTimePicker(
            options={
                'useCurrent': True,
                'timeZone': str(timezone.get_current_timezone()),
                'collapse': False,
                'minDate': str(timezone.now().astimezone().strftime("%Y-%m-%d 00:00:00")),
            }, attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
        now = timezone.now().astimezone().strftime("%Y-%m-%d %H:%M")
        self.fields['date_start'].help_text = f"Time Zone is {timezone.get_current_timezone()} ({now})"
        self.fields['date_stop'].help_text = f"Time Zone is {timezone.get_current_timezone()} ({now})"

    title = forms.CharField(label="Title",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    message = forms.CharField(label="Message",
                              widget=forms.Textarea(attrs={'class': 'form-control'}))

    date_start = forms.DateTimeField(label="Date start")

    date_stop = forms.DateTimeField(label="Date stop", help_text=f"Time Zone is {timezone.get_current_timezone()}")

    type = forms.ChoiceField(label="Type",
                             choices=AnnouncementType.choices,
                             initial=AnnouncementType.INFO,
                             widget=forms.Select(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super(AnnouncementForm, self).clean()
        date_start = cleaned_data.get("date_start")
        date_stop = cleaned_data.get("date_stop")
        now = timezone.now().astimezone()
        if date_start > date_stop:
            raise ValidationError({"date_start": "The start date must be earlier than the end date"})
        if date_start.date() < now.date():
            raise ValidationError({"date_start": "The start date must not be in the past"})

    class Meta:
        model = Announcement
        fields = ['title', 'message', 'date_start', 'date_stop', 'type']
