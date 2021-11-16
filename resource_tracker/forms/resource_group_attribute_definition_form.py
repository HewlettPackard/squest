from django.core.exceptions import ValidationError
from taggit.forms import *
from resource_tracker.models import ResourceGroupAttributeDefinition, ResourcePoolAttributeDefinition, \
    ExceptionResourceTracker
from utils.squest_model_form import SquestModelForm


class ResourceGroupAttributeDefinitionForm(SquestModelForm):
    class Meta:
        model = ResourceGroupAttributeDefinition
        fields = ["name", "help_text", "consume_from", "produce_for"]

    name = forms.CharField(label="Name",
                           widget=forms.TextInput())

    consume_from = forms.ModelChoiceField(queryset=ResourcePoolAttributeDefinition.objects.all(),
                                          required=False,
                                          widget=forms.Select())

    produce_for = forms.ModelChoiceField(queryset=ResourcePoolAttributeDefinition.objects.all(),
                                         required=False,
                                         widget=forms.Select())

    help_text = forms.CharField(label="Help text",
                                required=False,
                                max_length=ResourceGroupAttributeDefinition._meta.get_field('help_text').max_length,
                                widget=forms.TextInput())

    def clean(self):
        super(ResourceGroupAttributeDefinitionForm, self).clean()
        name = self.cleaned_data['name']
        if self.instance.id:  # we are editing
            if name != self.instance.name:
                self.raise_validation_error_if_name_exist(name)
        else:  # we are creating
            self.raise_validation_error_if_name_exist(name)
        return self.cleaned_data

    def raise_validation_error_if_name_exist(self, name):
        if ResourceGroupAttributeDefinition.objects.filter(name=name, resource_group=self.resource_group).exists():
            text_error = f"Attribute {name} already exist in {self.resource_group}"
            raise ValidationError({'name': text_error})
