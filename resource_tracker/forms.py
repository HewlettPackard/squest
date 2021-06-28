from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, ResourcePoolAttributeDefinition, \
    Resource, ResourceAttribute, ResourcePool


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

    def clean(self):
        cleaned_data = self.cleaned_data
        if hasattr(self, 'resource_group'):
            if ResourceGroupAttributeDefinition.objects.filter(name=cleaned_data['name'],
                                                               resource_group_definition=self.resource_group).exists():
                raise ValidationError({'name': ["Attribute with this name already exists for this resource", ]})

        # Always return cleaned_data
        return cleaned_data

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
        self._newly_created = kwargs.get('instance') is None

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
        if self._newly_created:
            self.instance = Resource.objects.create(name=resource_name, resource_group=self.resource_group)
        else:
            self.instance.name = resource_name
            self.instance.save()

        # get all attribute
        for attribute_name, value in self.cleaned_data.items():
            if attribute_name is not "name" and value is not None and value != "":
                self.instance.add_attribute(attribute_name)
                self.instance.set_attribute(attribute_name, value)

        return self.instance

    class Meta:
        model = Resource
        fields = ["name"]


class ResourcePoolForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ResourcePool
        fields = ["name"]


class ResourcePoolAttributeDefinitionForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = self.cleaned_data
        if hasattr(self, 'resource_pool'):
            if ResourcePoolAttributeDefinition.objects.filter(name=cleaned_data['name'],
                                                              resource_pool=self.resource_pool).exists():
                raise ValidationError({'name': ["Attribute with this name already exists for this resource pool", ]})

        # Always return cleaned_data
        return cleaned_data

    class Meta:
        model = ResourcePoolAttributeDefinition
        fields = ["name"]
