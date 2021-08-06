from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from taggit.forms import *
from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, ResourcePoolAttributeDefinition, \
    Resource, ResourceAttribute, ResourcePool
from service_catalog.models import Instance


class ResourceGroupForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    tags = TagField(label="Tags",
                    required=False,
                    help_text="Comma-separated list of tags (more details in documentation)",
                    widget=TagWidget(attrs={'class': 'form-control'}))

    class Meta:
        model = ResourceGroup
        fields = ["name", "tags"]


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

    service_catalog_instance = forms.ModelChoiceField(queryset=Instance.objects.all(),
                                                      label="Service catalog instance",
                                                      required=False,
                                                      widget=forms.Select(attrs={'class': 'form-control'}))

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
                                                                  attribute_type=attribute)
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
            self.instance = super(ResourceForm, self).save()
            self.instance.resource_group = self.resource_group
        else:
            self.instance.name = resource_name

        self.instance.save()

        # get all attribute
        list_attribute_to_skip = ["name", "service_catalog_instance"]
        for attribute_name, value in self.cleaned_data.items():
            if attribute_name not in list_attribute_to_skip and value is not None and value != "":
                self.instance.add_attribute(ResourceGroupAttributeDefinition.objects.
                                            get(name=attribute_name,
                                                resource_group_definition=self.resource_group))
                self.instance.set_attribute(ResourceGroupAttributeDefinition.objects.
                                            get(name=attribute_name,
                                                resource_group_definition=self.resource_group), value)

        return self.instance

    class Meta:
        model = Resource
        fields = ["name", "service_catalog_instance"]


class ResourcePoolForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    tags = TagField(label="Tags",
                    required=False,
                    help_text="Comma-separated list of tags (more details in documentation)",
                    widget=TagWidget(attrs={'class': 'form-control'}))

    class Meta:
        model = ResourcePool
        fields = ["name", "tags"]


class ResourcePoolAttributeDefinitionForm(ModelForm):
    name = forms.CharField(label="Name",
                           required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    over_commitment_producers = forms.FloatField(label="Over commitment for producers",
                                                 required=False,
                                                 initial=ResourcePoolAttributeDefinition._meta.get_field(
                                                     'over_commitment_producers').default,
                                                 help_text="All producers will produce X times more",

                                                 widget=forms.NumberInput(
                                                     attrs={'class': 'form-control', 'step': '0.1'}))

    over_commitment_consumers = forms.FloatField(label="Over commitment for consumers",
                                                 required=False,
                                                 initial=ResourcePoolAttributeDefinition._meta.get_field(
                                                     'over_commitment_consumers').default,

                                                 help_text="All consumers will consume X times more",
                                                 widget=forms.NumberInput(
                                                     attrs={'class': 'form-control', 'step': '0.1'}))

    def clean_over_commitment_producers(self):
        data = self.cleaned_data['over_commitment_producers']
        if not data:
            data = ResourcePoolAttributeDefinition._meta.get_field('over_commitment_producers').default
        return data

    def clean_over_commitment_consumers(self):
        data = self.cleaned_data['over_commitment_consumers']
        if not data:
            data = ResourcePoolAttributeDefinition._meta.get_field('over_commitment_consumers').default
        return data

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
        fields = ["name", "over_commitment_producers", "over_commitment_consumers"]
