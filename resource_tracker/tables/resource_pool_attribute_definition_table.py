from django_tables2 import TemplateColumn

from resource_tracker.models import ResourcePoolAttributeDefinition
from Squest.utils.squest_table import SquestTable


class ResourcePoolAttributeDefinitionTable(SquestTable):
    class Meta:
        model = ResourcePoolAttributeDefinition
        attrs = {"id": "resource_group_table", "class": "table squest-pagination-tables"}
        fields = ("name", "over_commitment_producers", "over_commitment_consumers", "actions")

    actions = TemplateColumn(template_name='custom_columns/generic_actions_with_parent.html',
                                orderable=False,
                                extra_context={
                                    'object_name': 'resource_pool_attribute',
                                    'app_name': 'resource_tracker'
                                }
                                )
