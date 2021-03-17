import requests
import towerlib
import urllib3
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from towerlib import Tower

from service_catalog.models import TowerServer, Service, JobTemplate, Operation, Request, Message

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

    auto_accept = forms.BooleanField(label="Auto accept",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    auto_process = forms.BooleanField(label="Auto process",
                                      required=False,
                                      widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    image = forms.ImageField(label="Choose a file",
                             required=False,
                             widget=forms.FileInput())

    class Meta:
        model = Service
        fields = ["name", "description", "job_template", "auto_accept", "auto_process", "image"]


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


class SurveySelectorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        operation_id = kwargs.get('operation_id')
        self.operation = Operation.objects.get(id=operation_id)
        # create each field from the survey
        for field_name, is_checked in self.operation.enabled_survey_fields.items():
            attributes = {'class': 'custom-control-input',
                          'id': field_name,
                          'checked': is_checked}
            self.fields[field_name] = forms.BooleanField(required=False,
                                                         widget=forms.CheckboxInput(attrs=attributes))

    def save(self):
        # update the end user survey
        for field, value in self.cleaned_data.items():
            self.operation.enabled_survey_fields[field] = value
        self.operation.save()


class MessageOnRequestForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        request_id = kwargs.pop('request_id', None)
        message_required = kwargs.pop('message_required', False)
        super(MessageOnRequestForm, self).__init__(*args, **kwargs)

        self.target_request = Request.objects.get(id=request_id)

        help_text = ""
        if not message_required:
            help_text = "Optional message"

        self.fields['message'] = forms.CharField(label="Message",
                                                 required=message_required,
                                                 help_text=help_text,
                                                 widget=forms.Textarea(attrs={'class': 'form-control'}))

    def save(self):
        message_content = self.cleaned_data["message"]
        Message.objects.create(sender=self.user, content=message_content, request=self.target_request)
