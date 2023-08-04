
from django_tables2 import TemplateColumn

from Squest.utils.squest_table import SquestTable
from resource_tracker_v2.models import Transformer


class TransformerTable(SquestTable):
    class Meta:
        model = Transformer
        attrs = {"id": "attribute_definition_table", "class": "table squest-pagination-tables"}
        fields = ("attribute", "consume_from", "on_attribute", "factor", "actions")

    attribute = TemplateColumn(
        verbose_name="Attribute",
        template_name='resource_tracker_v2/resource_group/custom_columns/resource_group_attributes_attribute_name.html',
        orderable=True)
    consume_from = TemplateColumn(
        verbose_name="Consume from",
        template_name='resource_tracker_v2/resource_group/custom_columns/resource_group_attributes_consume.html',
        orderable=True)
    on_attribute = TemplateColumn(
        verbose_name="On attribute",
        template_name='resource_tracker_v2/resource_group/custom_columns/resource_group_attributes_on_attribute.html',
        orderable=True)
    actions = TemplateColumn(template_name='resource_tracker_v2/resource_group/custom_columns/resource_group_attribute_actions.html', orderable=False)
