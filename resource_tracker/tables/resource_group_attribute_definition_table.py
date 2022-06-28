from django_tables2 import TemplateColumn

from resource_tracker.models import ResourceGroupAttributeDefinition
from Squest.utils.squest_table import SquestTable


class ResourceGroupAttributeDefinitionTable(SquestTable):
    class Meta:
        model = ResourceGroupAttributeDefinition
        attrs = {"id": "resource_group_attribute_def_table", "class": "table squest-pagination-tables"}
        fields = ("name", "consume_from", "produce_for", "actions")

    actions = TemplateColumn(template_name='custom_columns/generic_actions_with_parent.html',
                                orderable=False,
                                extra_context={
                                    'object_name': 'resource_group_attribute',
                                    'app_name': 'resource_tracker'
                                }
                                )
