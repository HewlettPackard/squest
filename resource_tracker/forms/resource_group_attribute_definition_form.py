from django.core.exceptions import ValidationError
from django.forms import ModelForm
from taggit.forms import *
from resource_tracker.models import ResourceGroupAttributeDefinition, ResourcePoolAttributeDefinition, \
    ExceptionResourceTracker


class ResourceGroupAttributeDefinitionForm(ModelForm):
    class Meta:
        model = ResourceGroupAttributeDefinition
        fields = ["name", "help_text", "consume_from", "produce_for"]

    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    consume_from = forms.ModelChoiceField(queryset=ResourcePoolAttributeDefinition.objects.all(),
                                          required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'}))

    produce_for = forms.ModelChoiceField(queryset=ResourcePoolAttributeDefinition.objects.all(),
                                         required=False,
                                         widget=forms.Select(attrs={'class': 'form-control'}))

    help_text = forms.CharField(label="Help text",
                                required=False,
                                max_length=ResourceGroupAttributeDefinition._meta.get_field('help_text').max_length,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

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
