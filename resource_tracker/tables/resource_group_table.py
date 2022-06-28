from django_tables2 import TemplateColumn

from resource_tracker.models import ResourceGroup
from Squest.utils.squest_table import SquestTable


class ResourceGroupTable(SquestTable):
    class Meta:
        model = ResourceGroup
        attrs = {"id": "resource_group_table", "class": "table squest-pagination-tables"}
        fields = ("name", "tags", "resources", "actions")

    tags = TemplateColumn(template_name='custom_columns/tags.html', orderable=False)
    resources = TemplateColumn(template_name='custom_columns/resource_group_resource.html', orderable=False)
    actions = TemplateColumn(template_name='custom_columns/resource_group_operations.html', orderable=False)
