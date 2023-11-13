from django_tables2 import TemplateColumn, LinkColumn

from Squest.utils.squest_table import SquestTable
from resource_tracker_v2.models import AttributeGroup


class AttributeGroupTable(SquestTable):
    class Meta:
        model = AttributeGroup
        attrs = {"id": "attribute_group_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description")

    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)
    name = LinkColumn()
