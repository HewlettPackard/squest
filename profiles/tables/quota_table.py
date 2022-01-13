from django_tables2 import TemplateColumn

from profiles.models import Quota
from Squest.utils.squest_table import SquestTable


class QuotaTable(SquestTable):
    class Meta:
        model = Quota
        attrs = {"id": "quota_table", "class": "table squest-pagination-tables"}
        fields = ("name", "attribute_definitions", "actions")
    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)
    attribute_definitions = TemplateColumn(template_name='custom_columns/attribute_list.html', orderable=False)
