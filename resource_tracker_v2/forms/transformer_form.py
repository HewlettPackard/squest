from django import forms
from django.forms import ModelChoiceField

from Squest.utils.squest_model_form import SquestModelForm
from resource_tracker_v2.models import AttributeDefinition, Transformer
from resource_tracker_v2.models.resource_group import ResourceGroup


class TransformerForm(SquestModelForm):

    class Meta:
        model = Transformer
        fields = ["attribute_definition", "consume_from_resource_group", "consume_from_attribute_definition", "factor",
                  "yellow_threshold_percent_consumed", "red_threshold_percent_consumed"]

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


    def clean(self):
        cleaned_data = super().clean()
        attribute_definition = cleaned_data.get("attribute_definition")
        consume_from_resource_group = cleaned_data.get("consume_from_resource_group")
        consume_from_attribute = cleaned_data.get("consume_from_attribute_definition")

        if consume_from_resource_group is not None and consume_from_attribute is None:
            raise forms.ValidationError(
                {"consume_from_attribute_definition": f"Select a target attribute to consume from"})
        if consume_from_resource_group is None and consume_from_attribute is not None:
            raise forms.ValidationError(
                {"consume_from_resource_group": f"Select a target resource group to consume from"})

        if consume_from_resource_group is not None and consume_from_attribute is not None:
            # check if the target attribute is defined as transformer
            if Transformer.objects.filter(resource_group=consume_from_resource_group,
                                          attribute_definition=consume_from_attribute).count() == 0:
                raise forms.ValidationError(
                    {"consume_from_attribute_definition": f"Selected attribute '{consume_from_attribute.name}' is not "
                                                          f"a valid attribute of the resource group "
                                                          f"'{consume_from_resource_group.name}'"})

            if Transformer.is_loop_consumption_detected(source_resource_group=self.source_resource_group,
                                                        source_attribute=attribute_definition,
                                                        target_resource_group=consume_from_resource_group,
                                                        target_attribute=consume_from_attribute):
                raise forms.ValidationError(
                    {"consume_from_attribute_definition": f"Circular loop detected on resource "
                                                          f"group '{self.source_resource_group.name}'"})
