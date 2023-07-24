from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import LinkColumn, Table

from profiles.models import Quota


class TeamQuotaLimitTable(Table):

    scope = LinkColumn()
    limit = LinkColumn()

    class Meta:
        model = Quota
        attrs = {"id": "quota_team_table", "class": "table squest-pagination-tables"}
        fields = ("scope", "limit")
