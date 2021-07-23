import re

import requests
import towerlib
import urllib3
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from towerlib import Tower

from profiles.models import BillingGroup
from service_catalog.forms.utils import get_choices_from_string
from service_catalog.models import TowerServer, Service, JobTemplate, Operation, Request, RequestMessage, Instance

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TowerServerForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    host = forms.CharField(label="Host",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': "awx.mydomain.net:8043"}))

    token = forms.CharField(label="Token",
                            required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    secure = forms.BooleanField(label="Is secure (https)",
                                initial=True,
                                required=False,
                                widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    ssl_verify = forms.BooleanField(label="SSL verify",
                                    initial=False,
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
        fields = ["name", "host", "token", "secure", "ssl_verify"]


class ServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['billing_group_id'].choices += [(g.id, g.name) for g in BillingGroup.objects.all()]

    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    job_template = forms.ModelChoiceField(queryset=JobTemplate.objects.all(),
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

    billing = forms.ChoiceField(
        label="Billing :",
        choices=[
            ('none', 'No billing'),
            ('defined', 'Define billing'),
            ('choice_restricted', 'User define billing (restricted)'),
            ('choice', 'User define billing (all billing group)')
        ],
        initial='defined',
        widget=forms.RadioSelect()
    )

    billing_group_id = forms.ChoiceField(
        label="Billing group defined",
        choices=[(None, None)],
        initial=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    billing_group_is_displayed = forms.BooleanField(
        label="Display the billing",
        initial=False,
        required=False,
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = Service
        fields = ["name", "description", "job_template", "auto_accept", "auto_process", "image",
                  "billing", "billing_group_id", "billing_group_is_displayed"]


class EditServiceForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    image = forms.ImageField(label="Choose a file",
                             required=False,
                             widget=forms.FileInput())

    class Meta:
        model = Service
        fields = ["name", "description", "image"]


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

    process_timeout_second = forms.IntegerField(required=True,
                                                initial=60,
                                                label="Process timeout (second)",
                                                widget=forms.TextInput(attrs={'class': 'form-control'}))

    auto_accept = forms.BooleanField(label="Auto accept",
                                     initial=False,
                                     required=False,
                                     widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    auto_process = forms.BooleanField(label="Auto process",
                                      initial=False,
                                      required=False,
                                      widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Operation
        fields = ["name", "description", "job_template", "type", "process_timeout_second",
                  "auto_accept", "auto_process"]


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
        if message_content is not None and message_content != "":
            RequestMessage.objects.create(sender=self.user, content=message_content, request=self.target_request)


class AcceptRequestForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        request_id = kwargs.pop('request_id', None)
        super(AcceptRequestForm, self).__init__(*args, **kwargs)
        self.target_request = Request.objects.get(id=request_id)

        # load user provided fields and add admin field if exist
        if "spec" in self.target_request.operation.job_template.survey:
            for survey_definition in self.target_request.operation.job_template.survey["spec"]:
                if survey_definition["type"] == "text":
                    new_field = forms.CharField(label=survey_definition['question_name'],
                                                required=survey_definition['required'],
                                                widget=forms.TextInput(attrs={'class': 'form-control'}))
                    new_field.group = self._get_field_group(field_name=survey_definition['variable'],
                                                            enabled_field=self.target_request.operation.enabled_survey_fields)
                    self.fields[survey_definition['variable']] = new_field

                if survey_definition["type"] == "multiplechoice":
                    new_field = forms. \
                        ChoiceField(label=survey_definition['question_name'],
                                    required=survey_definition['required'],
                                    choices=get_choices_from_string(survey_definition["choices"]),
                                    error_messages={'required': 'At least you must select one choice'},
                                    widget=forms.Select(attrs={'class': 'form-control'}))
                    new_field.group = self._get_field_group(field_name=survey_definition['variable'],
                                                            enabled_field=self.target_request.operation.enabled_survey_fields)
                    self.fields[survey_definition['variable']] = new_field

    @staticmethod
    def _get_field_group(field_name, enabled_field):
        if enabled_field[field_name]:
            return "User"
        return "Admin"

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            user_provided_survey_fields[field_key] = value
        # update the request
        self.target_request.fill_in_survey = user_provided_survey_fields
        self.target_request.accept()
        self.target_request.save()
        # reset the instance state if it was failed (in case of resetting the state)
        self.target_request.instance.reset_to_last_stable_state()
        self.target_request.instance.save()


class InstanceForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    spec = forms.JSONField(label="JSON Spec",
                           required=False,
                           widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Instance
        fields = ["name", "spec"]
