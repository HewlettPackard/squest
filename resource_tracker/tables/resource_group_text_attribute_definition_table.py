from django_tables2 import TemplateColumn

from Squest.utils.squest_table import SquestTable
from resource_tracker.models import ResourceGroupTextAttributeDefinition


class ResourceGroupTextAttributeDefinitionTable(SquestTable):
    class Meta:
        model = ResourceGroupTextAttributeDefinition
        attrs = {"id": "resource_group_text_attribute_table", "class": "table squest-pagination-tables"}
        fields = ("name", "operation")

    operations = TemplateColumn(template_name='custom_columns/generic_actions_with_parent.html',
                                orderable=False,
                                extra_context={
                                    'object_name': 'resource_group_text_attribute',
                                    'app_name': 'resource_tracker'
                                }
                                )
