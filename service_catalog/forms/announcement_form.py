from django import forms
from django.forms import ModelForm
from django.utils import timezone
from tempus_dominus.widgets import DateTimePicker

from service_catalog.models.bootstrap_type import BootstrapType
from service_catalog.models.announcement import Announcement


class AnnouncementForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields['date_start'].widget = DateTimePicker(
            options={
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
                'timeZone': str(timezone.get_current_timezone()),
                'collapse': False,
                'minDate': str(timezone.now().astimezone().strftime("%Y-%m-%d 00:00:00")),
            }, attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
        now = timezone.now().astimezone().strftime("%Y-%m-%d %H:%M")
        tz_name = timezone.get_current_timezone()
        help_text = f"Time Zone is {tz_name} ({now})"
        self.fields['date_start'].help_text = help_text
        self.fields['date_stop'].help_text = help_text

    title = forms.CharField(label="Title",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    message = forms.CharField(label="Message",
                              help_text="HTML supported",
                              widget=forms.Textarea(attrs={'class': 'form-control'}))

    date_start = forms.DateTimeField(label="Date start")

    date_stop = forms.DateTimeField(label="Date stop")

    type = forms.ChoiceField(label="Type",
                             choices=BootstrapType.choices,
                             initial=BootstrapType.INFO,
                             widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Announcement
        fields = ['title', 'message', 'date_start', 'date_stop', 'type']
