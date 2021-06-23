from django import forms
from django.forms import ModelForm

from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, ResourcePoolAttributeDefinition, \
    Resource, ResourceAttribute


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


class ResourceForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        resource_group_id = kwargs.pop('resource_group_id', None)
        self.resource_group = ResourceGroup.objects.get(id=resource_group_id)
        super(ResourceForm, self).__init__(*args, **kwargs)

        for attribute in self.resource_group.attribute_definitions.all():
            initial_value = None
            if self.instance is not None:
                try:
                    initial_value = ResourceAttribute.objects.get(resource=self.instance,
                                                                  name=attribute.name)
                except ResourceAttribute.DoesNotExist:
                    pass
            new_field = forms.CharField(label=attribute.name,
                                        required=False,
                                        initial=initial_value,
                                        widget=forms.TextInput(attrs={'class': 'form-control'}))

            self.fields[attribute.name] = new_field

    def save(self, **kwargs):
        resource_name = self.cleaned_data["name"]
        if self.instance is not None:
            resource = self.instance
            resource.name = resource_name
            resource.save()
        else:
            resource = Resource.objects.create(name=resource_name, resource_group=self.resource_group)
        # get all attribute
        for attribute_name, value in self.cleaned_data.items():
            if attribute_name is not "name" and value is not None and value != "":
                resource.add_attribute(attribute_name)
                resource.set_attribute(attribute_name, value)
        return resource

    class Meta:
        model = Resource
        fields = ["name"]

