from django.utils.html import format_html
from django_tables2 import LinkColumn, TemplateColumn

from Squest.utils.squest_table import SquestTable
from profiles.models import Quota


class QuotaTable(SquestTable):
    scope = LinkColumn()
    attribute_definition = LinkColumn()
    actions = TemplateColumn(template_name='generics/custom_columns/generic_delete.html',
                             orderable=False,
                             exclude_from_export=True)
    available = LinkColumn(orderable=False)
    consumed = LinkColumn(orderable=False)
    limit = LinkColumn()

    class Meta:
        model = Quota
        attrs = {"id": "quota_table", "class": "table squest-pagination-tables "}
        fields = ("scope", "attribute_definition", "limit", "consumed", "available")

    def render_consumed(self, value, record):
        link = record.get_absolute_url()
        return format_html(f'<a href="{link}" class="btn btn-default bg-sm">{value}</a>')

    def value_consumed(self, value, record):
        return value
