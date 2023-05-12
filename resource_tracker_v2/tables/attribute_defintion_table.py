from django_tables2 import TemplateColumn

from Squest.utils.squest_table import SquestTable
from resource_tracker_v2.models import AttributeDefinition


class AttributeDefinitionTable(SquestTable):
    class Meta:
        model = AttributeDefinition
        attrs = {"id": "attribute_definition_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "actions")

    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)
