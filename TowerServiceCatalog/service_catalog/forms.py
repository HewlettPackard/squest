import requests
import towerlib
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from towerlib import Tower

from .models import TowerServer

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TowerServerForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    host = forms.CharField(label="host",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    token = forms.CharField(label="Token",
                            required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    secure = forms.BooleanField(label="Is secure",
                                required=False,
                                widget=forms.CheckboxInput(attrs={'class': 'form-control', 'checked': 'true'}))

    ssl_verify = forms.BooleanField(label="SSL verify",
                                    required=False,
                                    widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        host = cleaned_data.get("host")
        token = cleaned_data.get("token")
        secure = cleaned_data.get("secure")
        ssl_verify = cleaned_data.get("ssl_verify")

        if host and token:
            try:
                Tower(host, None, None, secure=secure, ssl_verify=ssl_verify, token=token)
            except towerlib.towerlibexceptions.AuthFailed:
                raise ValidationError({"token": "Fail to authenticate with provided token"})
            except requests.exceptions.SSLError:
                raise ValidationError({"ssl_verify": "Certificate verify failed"})
            except requests.exceptions.ConnectionError:
                raise ValidationError({"url": "Unable to connect to {}".format(url)})

    class Meta:
        model = TowerServer
        fields = ["name", "host", "token", "secure", "ssl_verify"]
