from django import forms
from django.forms import ModelForm

from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, ResourcePoolAttributeDefinition


class ResourceGroupForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ResourceGroup
        fields = ["name"]


class ResourceGroupAttributeDefinitionForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    consume_from = forms.ModelChoiceField(queryset=ResourcePoolAttributeDefinition.objects.all(),
                                          to_field_name="id",
                                          required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'}))

    produce_for = forms.ModelChoiceField(queryset=ResourcePoolAttributeDefinition.objects.all(),
                                         to_field_name="id",
                                         required=False,
                                         widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ResourceGroupAttributeDefinition
        fields = ["name", "consume_from", "produce_for"]
