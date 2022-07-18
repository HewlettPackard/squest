from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A

from profiles.models import Team


class NotificationFilterTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = Team
        attrs = {"id": "notification_filter__table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")
