import requests
import towerlib
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from towerlib import Tower

from .models import TowerServer, Service, JobTemplate, Operation

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
                raise ValidationError({"host": "Unable to connect to {}".format(host)})

    class Meta:
        model = TowerServer
        fields = ["name", "host", "token", "secure", "ssl_verify"]


class ServiceForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    job_template = forms.ModelChoiceField(queryset=JobTemplate.objects.all(),
                                          to_field_name="name",
                                          widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Service
        fields = ["name", "description"]


class AddServiceOperationForm(ModelForm):
    choice_type = [('UPDATE', 'Update'),
                   ('DELETE', 'Delete')]

    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    job_template = forms.ModelChoiceField(queryset=JobTemplate.objects.all(),
                                          required=True,
                                          to_field_name="name",
                                          widget=forms.Select(attrs={'class': 'form-control'}))

    type = forms.ChoiceField(label="Type",
                             choices=choice_type,
                             required=True,
                             error_messages={'required': 'At least you must select one type'},
                             widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Operation
        fields = ["name", "description", "job_template", "type"]
