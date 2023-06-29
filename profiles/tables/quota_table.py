from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import tables

from profiles.models import Quota


class QuotaTable(tables.Table):

    class Meta:
        model = Quota
        attrs = {"id": "quota_table", "class": "table squest-pagination-tables "}
        fields = ("attribute_definition", "limit", "consumed", "available")

    def render_consumed(self, value, record):
        link = reverse("profiles:quota_details", kwargs={'scope_id': record.scope.id, 'quota_id': record.id})
        return format_html(f'<a href="{link}" class="btn btn-default bg-sm">{value}</a>')
