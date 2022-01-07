from profiles.models import QuotaAttributeDefinition
from Squest.utils.squest_filter import SquestFilter


class QuotaAttributeDefinitionFilter(SquestFilter):
    class Meta:
        model = QuotaAttributeDefinition
        fields = ['name']
