from django import forms

from Squest.utils.squest_model_form import SquestModelForm
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

    image = forms.ImageField(label="Choose a file",
                             required=False,
                             widget=forms.FileInput())

    external_support_url = forms.CharField(label="External support URL",
                                           help_text="Redirect support button to the given URL",
                                           widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
                                           required=False)

    class Meta:
        model = Service
        fields = ["name", "description", "image", "enabled",
                  "parent_portfolio", "external_support_url", "extra_vars", "description_doc"]
