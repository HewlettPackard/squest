from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import tables

from profiles.models import Quota


class TeamQuotaLimitTable(tables.Table):

    class Meta:
        model = Quota
        attrs = {"id": "quota_team_table", "class": "table squest-pagination-tables"}
        fields = ("scope", "limit")

    def render_limit(self, value, record):
        link = reverse("profiles:team_quota_edit", kwargs={'scope_id': record.scope.id})
        return format_html(f'<a href="{link}">{value}</a>')

    def render_scope(self, value, record):
        link = reverse("profiles:team_details", kwargs={'pk': record.scope.id})
        return format_html(f'<a href="{link}">{value}</a>')
