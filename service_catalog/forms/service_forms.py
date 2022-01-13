import urllib3
from django import forms
from profiles.models import BillingGroup
from service_catalog.models import Service, JobTemplate, Operation
from service_catalog.models.operations import OperationType
from Squest.utils.squest_model_form import SquestModelForm
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ServiceForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['billing_group_id'].choices += [(g.id, g.name) for g in BillingGroup.objects.all()]

    name = forms.CharField(label="Name",
                           widget=forms.TextInput())

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput())

    job_template = forms.ModelChoiceField(queryset=JobTemplate.objects.all(),
                                          widget=forms.Select())

    auto_accept = forms.BooleanField(label="Auto accept",
                                     required=False,
                                     widget=forms.CheckboxInput())

    auto_process = forms.BooleanField(label="Auto process",
                                      required=False,
                                      widget=forms.CheckboxInput())

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
        widget=forms.RadioSelect()
    )

    billing_group_id = forms.ChoiceField(
        label="Billing group defined",
        choices=[(None, None)],
        initial=None,
        required=False,
        widget=forms.Select()
    )

    billing_group_is_shown = forms.BooleanField(
        label="Show the billing group to customer",
        initial=False,
        required=False,
        widget=forms.CheckboxInput()
    )

    enabled = forms.BooleanField(label="Enabled",
                                 initial=True,
                                 required=False,
                                 widget=forms.CheckboxInput())

    def clean_billing_group_id(self):
        if not self.cleaned_data['billing_group_id']:
            return None
        return self.cleaned_data['billing_group_id']

    def save(self, commit=True):
        billing = self.cleaned_data.get('billing')
        if billing == 'restricted_billing_groups':
            self.instance.billing_group_is_shown = True
            self.instance.billing_group_is_selectable = True
            self.instance.billing_groups_are_restricted = True
        elif billing == 'all_billing_groups':
            self.instance.billing_group_is_shown = True
            self.instance.billing_group_is_selectable = True
            self.instance.billing_groups_are_restricted = False
        else:
            self.instance.billing_group_is_selectable = False
            self.instance.billing_groups_are_restricted = False
        return super(ServiceForm, self).save()

    class Meta:
        model = Service
        fields = ["name", "description", "job_template", "auto_accept", "auto_process", "image",
                  "billing", "billing_group_id", "billing_group_is_shown", "enabled"]


class EditServiceForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        super(EditServiceForm, self).__init__(*args, **kwargs)
        self.fields['billing_group_id'].choices += [(g.id, g.name) for g in BillingGroup.objects.all()]
        if self.instance.billing_groups_are_restricted and self.instance.billing_group_is_selectable:
            self.fields['billing'].initial = 'restricted_billing_groups'
        elif self.instance.billing_group_is_selectable:
            self.fields['billing'].initial = 'all_billing_groups'
        else:
            self.fields['billing'].initial = 'defined'
        if not self.instance.asert_create_operation_have_job_template():
            self.fields['enabled'].disabled = True
            self.fields['enabled'].help_text = \
                "To enable this service, please link a job template to the 'CREATE' operation."

    name = forms.CharField(label="Name",
                           widget=forms.TextInput())

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput())

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

    def clean_billing_group_id(self):
        if not self.cleaned_data['billing_group_id']:
            return None
        return self.cleaned_data['billing_group_id']

    def save(self, commit=True):
        billing = self.cleaned_data.get('billing')
        if billing == 'restricted_billing_groups':
            self.instance.billing_group_is_shown = True
            self.instance.billing_group_is_selectable = True
            self.instance.billing_groups_are_restricted = True
        elif billing == 'all_billing_groups':
            self.instance.billing_group_is_shown = True
            self.instance.billing_group_is_selectable = True
            self.instance.billing_groups_are_restricted = False
        else:
            self.instance.billing_group_is_selectable = False
            self.instance.billing_groups_are_restricted = False
        return super(EditServiceForm, self).save()

    class Meta:
        model = Service
        fields = ["name", "description", "image", "billing", "billing_group_id", "billing_group_is_shown", 'enabled']


class AddServiceOperationForm(SquestModelForm):
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
                           widget=forms.TextInput())

    description = forms.CharField(label="Description",
                                  required=False,
                                  widget=forms.TextInput())

    job_template = forms.ModelChoiceField(queryset=JobTemplate.objects.all(),
                                          widget=forms.Select())

    type = forms.ChoiceField(label="Type",
                             choices=[(None, None)],
                             error_messages={'required': 'At least you must select one type'},
                             widget=forms.Select())

    process_timeout_second = forms.IntegerField(initial=60,
                                                label="Process timeout (second)",
                                                widget=forms.TextInput())

    auto_accept = forms.BooleanField(label="Auto accept",
                                     initial=False,
                                     required=False,
                                     widget=forms.CheckboxInput())

    auto_process = forms.BooleanField(label="Auto process",
                                      initial=False,
                                      required=False,
                                      widget=forms.CheckboxInput())

    class Meta:
        model = Operation
        fields = ["name", "description", "job_template", "type", "process_timeout_second",
                  "auto_accept", "auto_process"]
