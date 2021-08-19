from django.forms import ModelForm
from taggit.forms import *
from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition, Resource, ResourceAttribute, \
    ResourceTextAttribute, ResourceGroupTextAttributeDefinition
from service_catalog.models import Instance


class ResourceForm(ModelForm):
    class Meta:
        model = Resource
        fields = ["name", "service_catalog_instance"]

    name = forms.CharField(label="Name",
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
        self.attributes_name_list = list()
        self.text_attributes_name_list = list()

        for attribute in self.resource_group.attribute_definitions.all():
            initial_value = None
            if self.instance is not None:
                try:
                    initial_value = ResourceAttribute.objects.get(resource=self.instance,
                                                                  attribute_type=attribute)
                except ResourceAttribute.DoesNotExist:
                    pass
            new_field = forms.IntegerField(label=attribute.name,
                                           min_value=0,
                                           required=False,
                                           initial=initial_value,
                                           help_text=attribute.help_text,
                                           widget=forms.TextInput(attrs={'class': 'form-control'}))
            self.fields[attribute.name] = new_field
            self.attributes_name_list.append(attribute.name)
        for text_attribute in self.resource_group.text_attribute_definitions.all():
            initial_value = None
            if self.instance is not None:
                try:
                    initial_value = ResourceTextAttribute.objects.get(resource=self.instance,
                                                                      text_attribute_type=text_attribute)
                except ResourceTextAttribute.DoesNotExist:
                    pass
            new_field = forms.CharField(label=text_attribute.name,
                                        max_length=500,
                                        required=False,
                                        initial=initial_value,
                                        help_text=text_attribute.help_text,
                                        widget=forms.TextInput(attrs={'class': 'form-control'}))

            self.fields[text_attribute.name] = new_field
            self.text_attributes_name_list.append(text_attribute.name)

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
        for attribute_name in self.attributes_name_list:
            value = self.cleaned_data[attribute_name]
            default = ResourceAttribute._meta.get_field('value').default
            my_value = default if (value is None or value == "") else value
            self.instance.set_attribute(
                ResourceGroupAttributeDefinition.objects.get(
                    name=attribute_name,
                    resource_group_definition=self.resource_group
                ),
                my_value
            )
        for text_attribute_name in self.text_attributes_name_list:
            value = self.cleaned_data[text_attribute_name]
            default = ResourceTextAttribute._meta.get_field('value').default

            my_value = default if (value is None or value == "") else value
            self.instance.set_text_attribute(
                ResourceGroupTextAttributeDefinition.objects.get(
                    name=text_attribute_name,
                    resource_group_definition=self.resource_group
                ),
                my_value
            )

        return self.instance
