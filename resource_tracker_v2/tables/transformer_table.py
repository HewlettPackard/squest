from django_tables2 import TemplateColumn, LinkColumn, Column

from Squest.utils.squest_table import SquestTable
from resource_tracker_v2.models import Transformer


class TransformerTable(SquestTable):
    class Meta:
        model = Transformer
        attrs = {"id": "attribute_definition_table", "class": "table squest-pagination-tables"}
        fields = ("attribute_definition__name", "consume_from_resource_group", "consume_from_attribute_definition",
                  "factor", "actions")

    attribute_definition__name = Column()
    consume_from_resource_group = LinkColumn()
    consume_from_attribute_definition = Column(verbose_name="On attribute")
    actions = TemplateColumn(
        template_name='resource_tracker_v2/resource_group/custom_columns/resource_group_attribute_actions.html',
        orderable=False)
