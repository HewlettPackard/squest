from django import forms
from django.forms import FloatField, ModelChoiceField

from Squest.utils.squest_model_form import SquestModelForm
from resource_tracker_v2.models import AttributeDefinition, Transformer
from resource_tracker_v2.models.resource_group import ResourceGroup


class TransformerForm(SquestModelForm):

    class Meta:
        model = Transformer
        fields = ["attribute_definition", "consume_from_resource_group", "consume_from_attribute_definition", "factor"]

    def __init__(self, *args, **kwargs):
        self.source_resource_group = kwargs.pop("source_resource_group")
        super(TransformerForm, self).__init__(*args, **kwargs)
        self.instance.resource_group = self.source_resource_group

        all_resource_group_except_current = ResourceGroup.objects.all().exclude(id=self.source_resource_group.id)
        all_attribute_except_one_already_linked = AttributeDefinition.objects.all().exclude(id__in=[transformer.attribute_definition.id for transformer in Transformer.objects.filter(resource_group_id=self.source_resource_group)])
        all_linked_to_rg_attributes = Transformer.objects.values('attribute_definition').distinct()
        available_attribute = AttributeDefinition.objects.all().filter(id__in=all_linked_to_rg_attributes)

        if self.instance.pk is not None:  # mode edit
            self.fields['attribute_definition'] = ModelChoiceField(label="Attribute",
                                                                   required=True,
                                                                   queryset=AttributeDefinition.objects.filter(id=self.instance.attribute_definition.id),
                                                                   disabled=True,
                                                                   initial=self.instance.attribute_definition,
                                                                   widget=forms.Select(attrs={'class': 'form-control'}))
        else:  # mode create
            self.fields['attribute_definition'] = ModelChoiceField(label="Attribute",
                                                                   required=True,
                                                                   queryset=all_attribute_except_one_already_linked.all(),
                                                                   widget=forms.Select(attrs={'class': 'form-control'}))

        self.fields['consume_from_resource_group'] = ModelChoiceField(label="Resource group to consume",
                                                                      required=False,
                                                                      queryset=all_resource_group_except_current.all(),
                                                                      widget=forms.Select(attrs={'class': 'form-control'}))

        self.fields['consume_from_attribute_definition'] = ModelChoiceField(label="Attribute to consume",
                                                                            required=False,
                                                                            queryset=available_attribute.all(),
                                                                            widget=forms.Select(attrs={'class': 'form-control'}))
        if self.instance.pk is not None and self.instance.consume_from_attribute_definition is not None:
            target_transformer = Transformer.objects.filter(resource_group=self.instance.consume_from_resource_group)
            self.fields['consume_from_attribute_definition'].choices = [(transformer.attribute_definition.id,
                                                                         transformer.attribute_definition.name) for transformer in target_transformer]

        self.fields["factor"] = FloatField(required=False,
                                           initial=1,
                                           widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        consume_from_resource_group = cleaned_data.get("consume_from_resource_group")
        consume_from_attribute = cleaned_data.get("consume_from_attribute_definition")

        if consume_from_resource_group is not None and consume_from_attribute is None:
            raise forms.ValidationError({"consume_from_attribute_definition": f"Select a target attribute to consume from"})

        if consume_from_resource_group is not None and consume_from_attribute is not None:
            # check if the target attribute is defined as transformer
            if Transformer.objects.filter(resource_group=consume_from_resource_group,
                                          attribute_definition=consume_from_attribute).count() == 0:
                raise forms.ValidationError({"consume_from_attribute_definition": f"Selected attribute '{consume_from_attribute.name}' is not a valid "
                                                                                  f"attribute of the resource group '{consume_from_resource_group.name}'"})

            # check for circular loop
            list_parent_id = list()
            next_transformer = Transformer.objects.filter(resource_group=consume_from_resource_group,
                                                          attribute_definition=consume_from_attribute).first()
            while next_transformer is not None and next_transformer.resource_group.id not in list_parent_id:
                list_parent_id.append(next_transformer.resource_group.id)
                next_transformer = next_transformer.get_parent()
            if next_transformer is not None and next_transformer.resource_group.id in list_parent_id:
                raise forms.ValidationError(f"Circular loop detected on resource "
                                            f"group '{next_transformer.resource_group.name}'")
