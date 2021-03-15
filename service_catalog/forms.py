import copy

import requests
import towerlib
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from towerlib import Tower

from .models import TowerServer, Service, JobTemplate, Operation

import urllib3

from .models.operations import OperationType

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

    image = forms.ImageField(label="Choose a file",
                             required=False,
                             widget=forms.FileInput())

    class Meta:
        model = Service
        fields = ["name", "description", "job_template", "image"]


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


class ServiceRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        service_id = kwargs.get('service_id')
        self.service = Service.objects.get(id=service_id)
        # get the create operation of this service
        self.create_operation = Operation.objects.get(service=self.service, type=OperationType.CREATE)

        # get all field that are not disabled by the admin
        purged_survey = self._get_available_fields(job_template_survey=self.create_operation.job_template.enabled_survey_fields,
                                                   operation_survey=self.create_operation.enabled_survey_fields)
        for survey_filed in purged_survey["spec"]:
            # todo: change form field type and widget depending on the survey field 'type'
            self.fields[survey_filed['variable']] = forms.CharField(label=survey_filed['question_name'],
                                                                    required=True,
                                                                    widget=forms.TextInput(attrs={'class': 'form-control'}))

    @staticmethod
    def _get_available_fields(job_template_survey, operation_survey):
        """
        Return survey fields from the job template that are active in the operation
        :return: survey dict
        :rtype dict
        """
        # copy the dict
        returned_dict = copy.copy(job_template_survey)
        # cleanup the list
        returned_dict["spec"] = list()
        # loop the original survey
        for survey_filed in job_template_survey["spec"]:
            if operation_survey[survey_filed["variable"]]:
                returned_dict["spec"].append(survey_filed)
        return returned_dict
