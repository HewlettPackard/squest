import re
import requests
import towerlib
from django import forms
from django.core.exceptions import ValidationError
from towerlib import Tower

from Squest.utils.squest_model_form import SquestModelForm
from service_catalog.models import TowerServer


class TowerServerForm(SquestModelForm):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput())

    host = forms.CharField(label="Host",
                           widget=forms.TextInput(attrs={'placeholder': "awx.mydomain.net:8043"}))

    token = forms.CharField(label="Token",
                            widget=forms.TextInput())

    secure = forms.BooleanField(label="Is secure (https)",
                                initial=True,
                                required=False,
                                widget=forms.CheckboxInput())

    ssl_verify = forms.BooleanField(label="SSL verify",
                                    initial=False,
                                    required=False,
                                    widget=forms.CheckboxInput())

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
                raise ValidationError({"host": f"Unable to connect to {host}"})

    def save(self, commit=True):
        instance = super(TowerServerForm, self).save(commit=False)
        regex = r"^(http[s]?://)?(?P<hostname>[A-Za-z0-9\-\.]+)(?P<port>:[0-9]+)?(?P<path>.*)$"
        matches = re.search(regex, instance.host)
        if matches.group("hostname") is not None:
            instance.host = matches.group("hostname")
        if matches.group("port") is not None:
            instance.host = instance.host + matches.group("port")
        if matches.group("path") is not None:
            instance.host = instance.host + matches.group("path")
        if instance.host[-1] == "/":  # remove trailing slash
            instance.host = instance.host[:-1]
        if commit:
            instance.save()
        return instance

    class Meta:
        model = TowerServer
        fields = ["name", "host", "token", "secure", "ssl_verify", "extra_vars"]
