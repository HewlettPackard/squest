from django import forms
from profiles.models import BillingGroup
from service_catalog.models import Service
from Squest.utils.squest_model_form import SquestModelForm


class ServiceForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['enabled'].disabled = True
        self.fields['enabled'].initial = False
        self.fields['billing_group_id'].choices += [(g.id, g.name) for g in BillingGroup.objects.all()]
        if self.instance.id: # Edit object
            self.fields['enabled'].initial = self.instance.enabled
            if self.instance.billing_groups_are_restricted and self.instance.billing_group_is_selectable:
                self.fields['billing'].initial = 'restricted_billing_groups'
            elif self.instance.billing_group_is_selectable:
                self.fields['billing'].initial = 'all_billing_groups'
            else:
                self.fields['billing'].initial = 'defined'
            self.fields['enabled'].disabled = False
            if not self.instance.can_be_enabled():
                self.fields['enabled'].disabled = True
                self.fields['enabled'].help_text = \
                    "'CREATE' operation with a job template is required to enable this service."

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

    external_support_url = forms.CharField(label="External support URL",
                                           help_text="Redirect support button to the given URL",
                                           widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
                                           required=False)

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
        new_service = super(ServiceForm, self).save()
        return new_service

    class Meta:
        model = Service
        fields = ["name", "description", "image", "billing", "billing_group_id", "billing_group_is_shown", "enabled",
                  "parent_portfolio", "external_support_url", "extra_vars", "description_doc"]
