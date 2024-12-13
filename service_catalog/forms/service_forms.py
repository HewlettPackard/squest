from django import forms
from django.forms import CharField, ModelChoiceField

from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import Permission
from service_catalog.forms.form_utils import FormUtils
from service_catalog.models.services import Service


class ServiceForm(SquestModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['enabled'].disabled = True
        self.fields['enabled'].initial = False
        if self.instance.id:  # Edit object
            self.fields['enabled'].initial = self.instance.enabled
            self.fields['enabled'].disabled = False
            if not self.instance.can_be_enabled():
                self.fields['enabled'].disabled = True
                self.fields['enabled'].help_text = \
                    "'CREATE' operation with a job template is required to enable this service."
            # set permission field. If one operation in the service is not using the default
            all_permission_current_service = Permission.objects.filter(operation__service=self.instance).distinct()
            if all_permission_current_service.count() > 1:
                set_at_operation_level = ('set_at_operation_level','OVERWRITTEN BY OPERATION')
                self.fields["permission"].choices = list(self.fields['permission'].choices) + [set_at_operation_level]
                self.fields["permission"].initial = set_at_operation_level
            else:
                self.fields["permission"].initial = all_permission_current_service.first()

    image = forms.ImageField(label="Choose a file",
                             required=False,
                             widget=forms.FileInput())

    external_support_url = forms.CharField(label="External support URL",
                                           help_text="Redirect support button to the given URL",
                                           widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
                                           required=False)
    permission = ModelChoiceField(
        queryset=Permission.objects.filter(content_type__model="operation", content_type__app_label="service_catalog"),
        initial=FormUtils.get_default_permission_for_operation,
    help_text="Applying a new permission here will apply it on all operations")

    def save(self, commit=True):
        # save as usual
        obj = super().save(commit)
        # bulk edit on permission
        new_perm = self.cleaned_data.get('permission')
        obj.bulk_set_permission_on_operation(new_perm)
        return obj

    class Meta:
        model = Service
        fields = ["name", "description", "image", "enabled",
                  "parent_portfolio", "external_support_url", "extra_vars", "description_doc", "attribute_definitions",
                  "permission"]