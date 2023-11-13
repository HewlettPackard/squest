from django.forms import CharField, TextInput

from Squest.utils.squest_model_form import SquestModelForm
from resource_tracker_v2.models import AttributeDefinition


class AttributeDefinitionForm(SquestModelForm):
    class Meta:
        model = AttributeDefinition
        fields = ["name", "description", "attribute_group"]

    name = CharField(label="Name", widget=TextInput())
    description = CharField(label="Description", widget=TextInput(), required=False)
