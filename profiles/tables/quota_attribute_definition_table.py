from django_tables2 import TemplateColumn

from profiles.models import QuotaAttributeDefinition
from Squest.utils.squest_table import SquestTable


class QuotaAttributeDefinitionTable(SquestTable):
    class Meta:
        model = QuotaAttributeDefinition
        attrs = {"id": "quota_attribute_definition_table", "class": "table squest-pagination-tables"}
        fields = ("name", "attribute_definitions", "actions")
    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)
    attribute_definitions = TemplateColumn(template_name='custom_columns/attribute_list.html', orderable=False)
