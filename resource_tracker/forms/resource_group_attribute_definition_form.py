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
        produce_for = self.cleaned_data['produce_for']
        consume_from = self.cleaned_data['consume_from']
        help_text = self.cleaned_data['help_text']
        if not self.instance.id:
            try:
                self.resource_group.add_attribute_definition(name, produce_for, consume_from, help_text)
            except ExceptionResourceTracker.AttributeAlreadyExist as e:
                raise ValidationError({'name': e})
        else:
            try:
                self.resource_group.edit_attribute_definition(self.instance.id, name, produce_for, consume_from,
                                                              help_text)
            except ExceptionResourceTracker.AttributeAlreadyExist as e:
                raise ValidationError({'name': e})
        return self.cleaned_data
