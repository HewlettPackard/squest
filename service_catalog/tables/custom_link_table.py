from django_tables2 import tables, TemplateColumn

from service_catalog.models import CustomLink


class CustomLinkTable(tables.Table):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = CustomLink
        attrs = {"id": "custom_link_table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")

    def render_name(self, record):
        return f"{record}"
