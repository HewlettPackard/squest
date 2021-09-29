from django.core.exceptions import ValidationError
from taggit.forms import *
from resource_tracker.models import ExceptionResourceTracker, ResourceGroupTextAttributeDefinition
from utils.squest_model_form import SquestModelForm


class ResourceGroupTextAttributeDefinitionForm(SquestModelForm):
    class Meta:
        model = ResourceGroupTextAttributeDefinition
        fields = ["name", "help_text"]

    name = forms.CharField(label="Name",
                           widget=forms.TextInput())

    help_text = forms.CharField(label="Help text",
                                required=False,
                                max_length=ResourceGroupTextAttributeDefinition._meta.get_field('help_text').max_length,
                                widget=forms.TextInput())

    def clean(self):
        super(ResourceGroupTextAttributeDefinitionForm, self).clean()
        name = self.cleaned_data['name']
        help_text = self.cleaned_data['help_text']

        if not self.instance.id:
            try:
                self.resource_group.add_text_attribute_definition(name, help_text)
            except ExceptionResourceTracker.AttributeAlreadyExist as e:
                raise ValidationError({'name': e})
        else:
            try:
                self.resource_group.edit_text_attribute_definition(self.instance.id, name, help_text)
            except ExceptionResourceTracker.AttributeAlreadyExist as e:
                raise ValidationError({'name': e})
        return self.cleaned_data
