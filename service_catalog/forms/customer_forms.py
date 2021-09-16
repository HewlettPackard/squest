import copy

import urllib3
from django import forms
from guardian.models import UserObjectPermission
from django.core.exceptions import ValidationError

from profiles.models import BillingGroup
from service_catalog.forms.utils import get_fields_from_survey
from service_catalog.models import Service, Operation, Instance, Request, Support, SupportMessage
from service_catalog.models.operations import OperationType

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FormUtils:

    @classmethod
    def get_available_fields(cls, job_template_survey, operation_survey):
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
        if "spec" in job_template_survey:
            for survey_filed in job_template_survey["spec"]:
                if operation_survey[survey_filed["variable"]]:
                    returned_dict["spec"].append(survey_filed)
        return returned_dict


class ServiceRequestForm(forms.Form):
    instance_name = forms.CharField(label="Squest instance name",
                                    help_text="Help to identify the requested service in the 'Instances' view",
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))

    billing_group_id = forms.ChoiceField(
        label="Billing group",
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'disabled': False})
    )

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        service_id = kwargs.pop('service_id', None)
        super(ServiceRequestForm, self).__init__(*args, **kwargs)

        self.service = Service.objects.get(id=service_id)
        if self.service.billing_groups_are_restricted:
            self.fields['billing_group_id'].choices = [(g.id, g.name) for g in self.user.billing_groups.all()]
        else:
            self.fields['billing_group_id'].choices = [(g.id, g.name) for g in BillingGroup.objects.all()]
        if not self.service.billing_group_is_selectable:
            self.fields['billing_group_id'].choices += [(None, None)]
            self.fields['billing_group_id'].widget.attrs['disabled'] = True
            self.fields['billing_group_id'].initial = self.service.billing_group_id
        if not self.service.billing_group_is_shown:
            self.fields['billing_group_id'].label = ""
            self.fields['billing_group_id'].widget = forms.HiddenInput()
        # get the create operation of this service
        self.create_operation = Operation.objects.get(service=self.service, type=OperationType.CREATE)

        # get all field that are not disabled by the admin
        purged_survey = FormUtils.get_available_fields(job_template_survey=self.create_operation.job_template.survey,
                                                       operation_survey=self.create_operation.enabled_survey_fields)
        self.fields.update(get_fields_from_survey(purged_survey))

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            user_provided_survey_fields[field_key] = value
        # create the instance
        instance_name = self.cleaned_data["instance_name"]
        billing_group_id = self.cleaned_data["billing_group_id"] if self.cleaned_data[
            "billing_group_id"] else self.service.billing_group_id
        billing_group = BillingGroup.objects.get(id=billing_group_id) if billing_group_id else None
        new_instance = Instance.objects.create(service=self.service, name=instance_name, billing_group=billing_group,
                                               spoc=self.user)
        # create the request
        new_request = Request.objects.create(instance=new_instance,
                                             operation=self.create_operation,
                                             fill_in_survey=user_provided_survey_fields,
                                             user=self.user)
        return new_request

    def clean_billing_group_id(self):
        if self.service.billing_group_is_selectable and not self.fields["billing_group_id"].choices:
            raise ValidationError('You must be in a billing group to request this service')

    def clean(self):
        super(ServiceRequestForm, self).clean()


class OperationRequestForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        operation_id = kwargs.pop('operation_id', None)
        instance_id = kwargs.pop('instance_id', None)
        super(OperationRequestForm, self).__init__(*args, **kwargs)

        self.operation = Operation.objects.get(id=operation_id)
        self.instance = Instance.objects.get(id=instance_id)

        # get all field that are not disabled by the admin
        purged_survey = FormUtils.get_available_fields(job_template_survey=self.operation.job_template.survey,
                                                       operation_survey=self.operation.enabled_survey_fields)
        self.fields = get_fields_from_survey(purged_survey)

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            user_provided_survey_fields[field_key] = value

        new_request = Request.objects.create(instance=self.instance,
                                             operation=self.operation,
                                             fill_in_survey=user_provided_survey_fields,
                                             user=self.user)
        # TODO: send notification to admins
        return new_request


class SupportRequestForm(forms.Form):
    title = forms.CharField(label="Title",
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    content = forms.CharField(label="Add a comment",
                              help_text="Markdown supported",
                              widget=forms.Textarea(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        instance_id = kwargs.pop('instance_id', None)
        super(SupportRequestForm, self).__init__(*args, **kwargs)
        self.instance = Instance.objects.get(id=instance_id)

    def save(self):
        title = self.cleaned_data["title"]
        content = self.cleaned_data["content"]
        # open a new support case
        new_support = Support.objects.create(title=title,
                                             instance=self.instance,
                                             user_open=self.user)

        SupportMessage.objects.create(content=content, sender=self.user, support=new_support)
