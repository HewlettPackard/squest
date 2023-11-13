from django_filters.fields import ModelMultipleChoiceField

from Squest.utils.squest_model_form import SquestModelForm
from resource_tracker_v2.models import AttributeGroup, AttributeDefinition


class AttributeGroupForm(SquestModelForm):
    class Meta:
        model = AttributeGroup
        fields = ["name", "description", "attribute_definitions"]

    attribute_definitions = ModelMultipleChoiceField(
        label="Attribute definitions",
        required=False,
        queryset=AttributeDefinition.objects.all()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['attribute_definitions'].initial = self.instance.attribute_definitions.all()

    def save(self, commit=True):
        attribute_group = super().save(commit=True)
        attribute_group.attribute_definitions.set(self.cleaned_data['attribute_definitions'])
        return attribute_group
