from django_tables2 import TemplateColumn

from Squest.utils.squest_table import SquestTable
from service_catalog.models import CustomLink


class CustomLinkTable(SquestTable):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = CustomLink
        attrs = {"id": "custom_link_table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")

    def render_name(self, record):
        return f"{record}"
