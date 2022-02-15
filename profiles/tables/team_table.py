from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A

from profiles.models import Team


class TeamTable(tables.Table):
    name = LinkColumn("profiles:team_details", args=[A("id")])
    actions = TemplateColumn(template_name='custom_columns/team_actions.html', orderable=False)

    class Meta:
        model = Team
        attrs = {"id": "team_table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")
