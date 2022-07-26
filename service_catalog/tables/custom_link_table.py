from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A

from service_catalog.models import CustomLink


class CustomLinkTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = CustomLink
        attrs = {"id": "custom_link_table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")
