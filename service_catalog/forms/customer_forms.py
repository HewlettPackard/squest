import copy

import urllib3
from django import forms
from guardian.models import UserObjectPermission

from service_catalog.models import Service, Operation, Instance, Request
from service_catalog.models.operations import OperationType

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ServiceRequestForm(forms.Form):

    instance_name = forms.CharField(label="Instance name",
                                    required=True,
                                    help_text="Help to identify the requested service in the 'Instances' view",
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        # get arguments from instance
        self.user = user
        service_id = kwargs.pop('service_id', None)
        super(ServiceRequestForm, self).__init__(*args, **kwargs)

        self.service = Service.objects.get(id=service_id)
        # get the create operation of this service
        self.create_operation = Operation.objects.get(service=self.service, type=OperationType.CREATE)

        # get all field that are not disabled by the admin
        purged_survey = self._get_available_fields(job_template_survey=self.create_operation.job_template.survey,
                                                   operation_survey=self.create_operation.enabled_survey_fields)
        for survey_filed in purged_survey["spec"]:
            if survey_filed["type"] == "text":
                self.fields[survey_filed['variable']] = forms. \
                    CharField(label=survey_filed['question_name'],
                              required=survey_filed['required'],
                              widget=forms.TextInput(attrs={'class': 'form-control'}))

            if survey_filed["type"] == "multiplechoice":
                self.fields[survey_filed['variable']] = forms. \
                    ChoiceField(label="Type",
                                required=survey_filed['required'],
                                choices=self._get_choices_from_string(survey_filed["choices"]),
                                error_messages={'required': 'At least you must select one choice'},
                                widget=forms.Select(attrs={'class': 'form-control'}))

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            user_provided_survey_fields[field_key] = value
        # create the instance
        instance_name = self.cleaned_data["instance_name"]
        new_instance = Instance.objects.create(service=self.service, name=instance_name)
        # give user perm on this instance
        UserObjectPermission.objects.assign_perm('change_instance', self.user, obj=new_instance)
        UserObjectPermission.objects.assign_perm('view_instance', self.user, obj=new_instance)
        # create the request
        new_request = Request.objects.create(instance=new_instance,
                                             operation=self.create_operation,
                                             fill_in_survey=user_provided_survey_fields)
        UserObjectPermission.objects.assign_perm('view_request', self.user, obj=new_request)
        UserObjectPermission.objects.assign_perm('delete_request', self.user, obj=new_request)
        # TODO: send notification to admins
        return new_request

    def clean(self):
        super(ServiceRequestForm, self).clean()

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

    @staticmethod
    def _get_choices_from_string(string_with_anti_slash_n):
        split_lines = string_with_anti_slash_n.splitlines()
        returned_list = list()
        for line in split_lines:
            returned_list.append((line, line))
        return returned_list
