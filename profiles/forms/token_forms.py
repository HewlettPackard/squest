from django import forms
from django.utils import timezone
from tempus_dominus.widgets import DateTimePicker

from profiles.models import Token


class TokenForm(forms.ModelForm):
    class Meta:
        model = Token
        fields = ['description', 'expires']

    def __init__(self, *args, **kwargs):
        super(TokenForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['expires'].widget = DateTimePicker(
            options={
                'useCurrent': True,
                'timeZone': str(timezone.get_current_timezone()),
                'collapse': False,
                'minDate': str(timezone.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")),
            }, attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
