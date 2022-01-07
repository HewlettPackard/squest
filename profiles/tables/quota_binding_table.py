from django_tables2 import TemplateColumn

from profiles.models import QuotaBinding
from Squest.utils.squest_table import SquestTable


class QuotaBindingTable(SquestTable):
    class Meta:
        model = QuotaBinding
        attrs = {"id": "quota_table", "class": "table squest-pagination-tables"}
        fields = ("quota_attribute_definition__name", "percentage", "consumed", "limit", "available", "actions")

    actions = TemplateColumn(template_name='custom_columns/generic_actions_with_parent.html', orderable=False)
    percentage = TemplateColumn(template_name='custom_columns/quota_percentage.html')
    available = TemplateColumn(template_name='custom_columns/quota_available.html')
