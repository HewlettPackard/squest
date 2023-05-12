from django_tables2 import TemplateColumn

from Squest.utils.squest_table import SquestTable
from resource_tracker_v2.models import ResourceGroup


class ResourceGroupTable(SquestTable):
    class Meta:
        model = ResourceGroup
        attrs = {"id": "resource_group_table", "class": "table squest-pagination-tables"}
        fields = ("name", "tags", "attributes", "resources", "actions")

    tags = TemplateColumn(template_name='custom_columns/tags.html', orderable=False)
    attributes = TemplateColumn(
        template_name='resource_tracking_v2/resource_group/custom_columns/resource_group_attributes.html',
        orderable=False)
    resources = TemplateColumn(
        template_name='resource_tracking_v2/resource_group/custom_columns/resource_group_resource.html',
        orderable=False)
    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)
