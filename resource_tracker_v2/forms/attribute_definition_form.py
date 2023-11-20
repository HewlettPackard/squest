from django.forms import ModelMultipleChoiceField

from Squest.utils.squest_model_form import SquestModelForm
from resource_tracker_v2.models import AttributeDefinition
from service_catalog.models import Service


class AttributeDefinitionForm(SquestModelForm):
    class Meta:
        model = AttributeDefinition
        fields = ["name", "description"]

    services = ModelMultipleChoiceField(queryset=Service.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(AttributeDefinitionForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['services'].initial = [service for service in self.instance.services.all()]

    def save(self, commit=True):
        attribute_definition = super().save(commit)
        attribute_definition.services.set(self.cleaned_data['services'])
        return attribute_definition
