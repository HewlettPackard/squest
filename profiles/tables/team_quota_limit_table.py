from django_tables2 import LinkColumn

from Squest.utils.squest_table import SquestTable
from profiles.models import Quota


class TeamQuotaLimitTable(SquestTable):
    scope = LinkColumn()
    limit = LinkColumn()
    consumed = LinkColumn(orderable=False)

    class Meta:
        model = Quota
        attrs = {"id": "quota_team_table", "class": "table squest-pagination-tables"}
        fields = ("scope", "limit", "consumed")
