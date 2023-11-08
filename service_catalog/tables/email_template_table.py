from django_tables2 import TemplateColumn, LinkColumn

from Squest.utils.squest_table import SquestTable
from service_catalog.models import EmailTemplate


class EmailTemplateTable(SquestTable):
    name = LinkColumn()
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = EmailTemplate
        attrs = {"id": "custom_link_table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")
