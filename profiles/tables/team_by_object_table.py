from django_tables2 import tables, TemplateColumn
from profiles.models.team import Team


class TeamsByObjectTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/team_by_group_actions.html', orderable=False)
    role = TemplateColumn(template_name='custom_columns/role_object.html', orderable=False)

    class Meta:
        model = Team
        attrs = {"id": "teams_by_object_table", "class": "table squest-pagination-tables "}
        fields = ("name", "role", "actions")
