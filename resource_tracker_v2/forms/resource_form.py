from taggit.forms import *
from resource_tracker_v2.models import ResourceGroup, Resource, ResourceAttribute, AttributeDefinition
from Squest.utils.squest_model_form import SquestModelForm


class ResourceForm(SquestModelForm):
    class Meta:
        model = Resource
        fields = ["name", "service_catalog_instance", "is_deleted_on_instance_deletion"]

    def __init__(self, *args, **kwargs):
        resource_group_id = kwargs.pop('resource_group_id', None)
        self.resource_group = ResourceGroup.objects.get(id=resource_group_id)
        super(ResourceForm, self).__init__(*args, **kwargs)
        self._newly_created = kwargs.get('instance') is None
        self.attributes_name_list = list()
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
        resource_name = self.cleaned_data["name"]
        if self._newly_created:
            self.instance = super(ResourceForm, self).save(commit=False)
            self.instance.resource_group = self.resource_group
        else:
            self.instance.name = resource_name

        self.instance.save()

        # get all attribute
        for attribute_name in self.attributes_name_list:
            value = self.cleaned_data[attribute_name]
            default = ResourceAttribute._meta.get_field('value').default
            my_value = default if (value is None or value == "") else value
            self.instance.set_attribute(AttributeDefinition.objects.get(name=attribute_name), my_value)

        return self.instance
