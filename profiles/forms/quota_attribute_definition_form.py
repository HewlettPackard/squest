from Squest.utils.squest_model_form import SquestModelForm
from profiles.models import QuotaAttributeDefinition


class QuotaAttributeDefinitionForm(SquestModelForm):
    class Meta:
        model = QuotaAttributeDefinition
        fields = ["name", "attribute_definitions"]
