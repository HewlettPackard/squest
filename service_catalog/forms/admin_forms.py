import re

import requests
import towerlib
import urllib3
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ChoiceField
from martor.fields import MartorFormField
from martor.widgets import AdminMartorWidget
from towerlib import Tower

from profiles.models import BillingGroup
from service_catalog.forms.utils import get_fields_from_survey, prefill_form_with_user_values
from service_catalog.models import TowerServer, Service, JobTemplate, Operation, Request, RequestMessage, Instance, \
    GlobalHook
from service_catalog.models.documentation import Doc
from service_catalog.models.instance import InstanceState
from service_catalog.models.operations import OperationType
from service_catalog.models.request import RequestState
from service_catalog.models.state_hooks import HookModel

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TowerServerForm(ModelForm):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    host = forms.CharField(label="Host",
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': "awx.mydomain.net:8043"}))

    token = forms.CharField(label="Token",
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
            ('defined', 'Define billing'),
            ('User define billing', (
                ('restricted_billing_groups', 'Restricted billing groups'),
                ('all_billing_groups', 'All billing groups')
            ))
        ],
        initial='defined',
        widget=forms.RadioSelect(attrs={'class': 'disable_list_style'})
    )

    billing_group_id = forms.ChoiceField(
        label="Billing group defined",
        choices=[(None, None)],
        initial=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    billing_group_is_shown = forms.BooleanField(
        label="Show the billing group to customer",
        initial=False,
        required=False,
        widget=forms.CheckboxInput()
    )

    def save(self, commit=True):
        service = super(ServiceForm, self).save(commit=False)
        billing = self.cleaned_data.get('billing')
        return save_service(service, commit, billing)

    class Meta:
        model = Service
        fields = ["name", "description", "job_template", "auto_accept", "auto_process", "image",
                  "billing", "billing_group_id", "billing_group_is_shown"]


class EditServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditServiceForm, self).__init__(*args, **kwargs)
        self.fields['billing_group_id'].choices += [(g.id, g.name) for g in BillingGroup.objects.all()]
        if self.instance.billing_groups_are_restricted and self.instance.billing_group_is_selectable:
            self.fields['billing'].initial = 'restricted_billing_groups'
        elif self.instance.billing_group_is_selectable:
            self.fields['billing'].initial = 'all_billing_groups'
        else:
            self.fields['billing'].initial = 'defined'

    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    image = forms.ImageField(label="Choose a file",
                             required=False,
                             widget=forms.FileInput())

    billing = forms.ChoiceField(
        label="Billing :",
        choices=[
            ('defined', 'Admin defined billing'),
            ('User defined billing', (
                ('restricted_billing_groups', 'Restricted billing groups'),
                ('all_billing_groups', 'All billing groups')
            ))
        ],
        initial='defined',
        widget=forms.RadioSelect(attrs={'class': 'disable_list_style'})
    )

    billing_group_id = forms.ChoiceField(
        label="Billing group defined",
        choices=[(None, None)],
        initial=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    billing_group_is_shown = forms.BooleanField(
        label="Show the billing group to customer",
        initial=False,
        required=False,
        widget=forms.CheckboxInput()
    )

    def save(self, commit=True):
        service = super(EditServiceForm, self).save(commit=False)
        billing = self.cleaned_data.get('billing')
        return save_service(service, commit, billing)

    class Meta:
        model = Service
        fields = ["name", "description", "image", "billing", "billing_group_id", "billing_group_is_shown"]


class AddServiceOperationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddServiceOperationForm, self).__init__(*args, **kwargs)
        choice_type_others = [('UPDATE', 'Update'),
                              ('DELETE', 'Delete')]

        choice_type_creation = [('CREATE', 'Create')]
        # Default behavior
        self.fields['type'].initial = choice_type_others[0]
        self.fields['type'].choices = choice_type_others

        if self.instance.id:  # if we have an operation
            if self.instance.type == OperationType.CREATE:
                self.fields['type'].initial = choice_type_creation[0]
                self.fields['type'].choices = choice_type_creation

    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    job_template = forms.ModelChoiceField(queryset=JobTemplate.objects.all(),
                                          widget=forms.Select(attrs={'class': 'form-control'}))

    type = forms.ChoiceField(label="Type",
                             choices=[(None, None)],
                             error_messages={'required': 'At least you must select one type'},
                             widget=forms.Select(attrs={'class': 'form-control'}))

    process_timeout_second = forms.IntegerField(initial=60,
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
            self.fields = get_fields_from_survey(self.target_request.operation.job_template.survey,
                                                 self.target_request.operation.enabled_survey_fields)
            prefill_form_with_user_values(self.fields, self.target_request.fill_in_survey)

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
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    spec = forms.JSONField(label="JSON Spec",
                           required=False,
                           widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Instance
        fields = ["name", "spec"]


def save_service(service, commit, billing):
    if not service.billing_group_id:
        service.billing_group_id = None
    if billing == 'restricted_billing_groups':
        service.billing_group_is_shown = True
        service.billing_group_is_selectable = True
        service.billing_groups_are_restricted = True
    elif billing == 'all_billing_groups':
        service.billing_group_is_shown = True
        service.billing_group_is_selectable = True
        service.billing_groups_are_restricted = False
    else:
        service.billing_group_is_selectable = False
        service.billing_groups_are_restricted = False
    if commit:
        service.save()
    return service


class GlobalHookForm(ModelForm):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    model = ChoiceField(label="Model",
                        choices=HookModel.choices,
                        error_messages={'required': 'At least you must select one model'},
                        widget=forms.Select(attrs={'class': 'form-control'}))

    state = ChoiceField(label="State",
                        choices=InstanceState.choices + RequestState.choices,
                        error_messages={'required': 'At least you must select one state'},
                        widget=forms.Select(attrs={'class': 'form-control'}))

    job_template = forms.ModelChoiceField(queryset=JobTemplate.objects.all(),
                                          widget=forms.Select(attrs={'class': 'form-control'}))

    extra_vars = forms.JSONField(label="Extra vars (JSON)",
                                 initial=dict(),
                                 required=False,
                                 widget=forms.Textarea(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super(GlobalHookForm, self).clean()
        model = cleaned_data.get('model')
        state = cleaned_data.get('state')

        choices = ""
        if model == "Request":
            choices = RequestState.choices
        if model == "Instance":
            choices = InstanceState.choices
        if state not in (choice[0] for choice in choices):
            raise ValidationError({
                'state': f"'{state}' is not a valid state of model '{model}'"
            })
        return cleaned_data

    class Meta:
        model = GlobalHook
        fields = ["name", "model", "state", "job_template", "extra_vars"]


class DocForm(ModelForm):
    title = forms.CharField(label="Name",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    content = MartorFormField(widget=AdminMartorWidget())

    class Meta:
        model = Doc
        fields = '__all__'
