from django.utils.html import format_html
from django_tables2 import LinkColumn, Table

from Squest.utils.squest_table import SquestTable
from profiles.models import Quota


class QuotaTable(SquestTable):
    scope = LinkColumn()
    attribute_definition = LinkColumn()

    class Meta:
        model = Quota
        attrs = {"id": "quota_table", "class": "table squest-pagination-tables "}
        fields = ("scope", "attribute_definition", "limit", "consumed", "available")

    def render_consumed(self, value, record):
        link = record.get_absolute_url()
        return format_html(f'<a href="{link}" class="btn btn-default bg-sm">{value}</a>')
