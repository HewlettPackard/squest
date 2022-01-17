
import urllib3
from django import forms
from django.core.exceptions import ValidationError

from profiles.models import BillingGroup
from service_catalog.forms.form_utils import FormUtils
from service_catalog.forms.utils import get_fields_from_survey
from service_catalog.models import Service, Operation, Instance, Request, RequestMessage
from service_catalog.models.operations import OperationType

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FIRST_BLOCK_FORM_FIELD_TITTLE = "1. Squest fields"
EXCLUDED_SURVEY_FIELDS = ["billing_group_id", "request_comment", "instance_name"]


class ServiceRequestForm(forms.Form):
    instance_name = forms.CharField(label="Squest instance name",
                                    help_text="Help to identify the requested service in the 'Instances' view",
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))

    request_comment = forms.CharField(label="Comment",
                                      help_text="Add a comment to your request",
                                      widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                                      required=False)

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
        self.fields['instance_name'].form_title = FIRST_BLOCK_FORM_FIELD_TITTLE

    def save(self):
        user_provided_survey_fields = dict()
        for field_key, value in self.cleaned_data.items():
            if field_key not in EXCLUDED_SURVEY_FIELDS:
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

        # save the comment
        request_comment = self.cleaned_data["request_comment"] if self.cleaned_data["request_comment"] else None
        if request_comment is not None:
            RequestMessage.objects.create(request=new_request, sender=self.user, content=request_comment)

        return new_request

    def clean_billing_group_id(self):
        if self.service.billing_group_is_selectable and (not self.fields["billing_group_id"].choices or not self.cleaned_data['billing_group_id']):
            raise ValidationError('You must be in a billing group to request this service')
        billing_group_id = self.cleaned_data['billing_group_id']
        return billing_group_id

    def clean(self):
        super(ServiceRequestForm, self).clean()
