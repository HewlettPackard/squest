from django import forms

from Squest.utils.squest_model_form import SquestModelForm
from resource_tracker_v2.models import Resource, ResourceAttribute, AttributeDefinition


class ResourceForm(SquestModelForm):
    class Meta:
        model = Resource
        fields = ["name", "service_catalog_instance", "is_deleted_on_instance_deletion", "resource_group"]

    def __init__(self, *args, **kwargs):
        self.resource_group = kwargs.pop('resource_group', None)
        super(ResourceForm, self).__init__(*args, **kwargs)
        self.attributes_name_list = list()
        self.fields['resource_group'].widget = forms.HiddenInput()
        self.fields['resource_group'].initial = self.resource_group.id
        for transformer in self.resource_group.transformers.all():
            initial_value = None
            if self.instance is not None:
                try:
                    initial_value = ResourceAttribute.objects.get(resource=self.instance,
                                                                  attribute_definition=transformer.attribute_definition)
                except ResourceAttribute.DoesNotExist:
                    pass
            new_field = forms.IntegerField(label=transformer.attribute_definition.name,
                                           min_value=0,
                                           required=False,
                                           initial=initial_value,
                                           help_text=transformer.attribute_definition.description,
                                           widget=forms.TextInput(attrs={'class': 'form-control'}))
            self.fields[transformer.attribute_definition.name] = new_field

            self.attributes_name_list.append(transformer.attribute_definition.name)

    def save(self, **kwargs):
        kwargs["commit"] = True
        self.instance = super(ResourceForm, self).save(kwargs)

        # get all attribute
        for attribute_name in self.attributes_name_list:
            value = self.cleaned_data[attribute_name]
            default = ResourceAttribute._meta.get_field('value').default
            my_value = default if (value is None or value == "") else value
            self.instance.set_attribute(AttributeDefinition.objects.get(name=attribute_name), my_value)

        return self.instance


class ResourceMoveForm(SquestModelForm):
    class Meta:
        model = Resource
        fields = ["resource_group"]
