from django import forms
from django.core.exceptions import ValidationError
from django.forms import ChoiceField, FloatField

from resource_tracker_v2.models import AttributeDefinition, Transformer
from resource_tracker_v2.models.resource_group import ResourceGroup


class ResourceGroupLinkForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.source_resource_group = kwargs.pop("source_resource_group")
        super(ResourceGroupLinkForm, self).__init__(*args, **kwargs)

        all_resource_group_except_current = ResourceGroup.objects.all().exclude(id=self.source_resource_group.id)
        all_attribute_except_one_already_linked = AttributeDefinition.objects.all().exclude(id__in=[att_def.id for att_def in self.source_resource_group.attribute_definitions.all()])
        all_linked__to_rg_attributes = ResourceGroup.objects.values('attribute_definitions').distinct()
        available_attribute = AttributeDefinition.objects.all().filter(id__in=all_linked__to_rg_attributes)

        self.fields['source_attribute_id'] = ChoiceField(label="Attribute",
                                                         required=True,
                                                         choices=[(attribute.pk, attribute.name) for attribute in all_attribute_except_one_already_linked],
                                                         widget=forms.Select(attrs={'class': 'form-control'}))

        self.fields['consume_from_resource_group_id'] = ChoiceField(label="Resource group to consume",
                                                                    required=False,
                                                                    choices=[("", "----------")] + [(resource_group.pk, resource_group.name) for resource_group in all_resource_group_except_current],
                                                                    widget=forms.Select(attrs={'class': 'form-control'}))

        self.fields['consume_from_attribute_id'] = ChoiceField(label="Attribute to consume",
                                                               required=False,
                                                               choices=[("", "----------")] + [(attribute.pk, attribute.name) for attribute in available_attribute],
                                                               widget=forms.Select(attrs={'class': 'form-control'}))

        self.fields["factor"] = FloatField(required=False,
                                           initial=1,
                                           widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}))

    # def clean(self):
    #     """
    #     checks:
    #     - target attribute is a valid attribute of the target RG
    #     - if RG not None then attribute not none
    #     """
    #     cleaned_data = super().clean()
    #
    #     # check source attribute exist (from given id)
    #     source_attribute_id = cleaned_data.get("source_attribute_id")
    #     consume_from_resource_group_id = cleaned_data.get("consume_from_resource_group_id")
    #     consume_from_attribute_id = cleaned_data.get("consume_from_attribute_id")
    #     if (consume_from_resource_group_id is not None and consume_from_resource_group_id != "") and (consume_from_attribute_id is not None and consume_from_attribute_id != ""):
    #         if Transformer.objects.filter(source_resource_group=self.source_resource_group,
    #                                       source_attribute_definition_id=consume_from_resource_group_id,
    #                                       destination_resource_group_id=consume_from_resource_group_id,
    #                                       destination_attribute_definition_id=consume_from_attribute_id).exists():
    #             raise ValidationError("source_attribute_id", "This link exist already")

    def save(self):
        source_attribute_id = self.cleaned_data.get('source_attribute_id')
        consume_from_resource_group_id = self.cleaned_data.get('consume_from_resource_group_id')
        consume_from_attribute_id = self.cleaned_data.get('consume_from_attribute_id')
        factor = self.cleaned_data.get('factor')

        source_attribute = AttributeDefinition.objects.get(id=source_attribute_id)
        if source_attribute not in self.source_resource_group.attribute_definitions.all():
            self.source_resource_group.attribute_definitions.add(source_attribute)
            self.source_resource_group.save()

        if (consume_from_resource_group_id is not None and consume_from_resource_group_id != "") and (consume_from_attribute_id is not None and consume_from_attribute_id != ""):
            if factor is None:
                factor = 1
            Transformer.objects.create(source_resource_group=self.source_resource_group,
                                       source_attribute_definition=source_attribute,
                                       destination_resource_group_id=consume_from_resource_group_id,
                                       destination_attribute_definition_id=consume_from_attribute_id,
                                       factor=factor)
        return self.source_resource_group
