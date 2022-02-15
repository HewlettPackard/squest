from django_tables2 import tables, Column, TemplateColumn
from profiles.models import TeamRoleBinding


class RoleBindingByTeamTable(tables.Table):
    object_name = Column(verbose_name='Name')
    actions = TemplateColumn(template_name='custom_columns/generic_delete_with_parent.html', orderable=False,
                             extra_context={'object_name': 'team_role_binding'})

    class Meta:
        model = TeamRoleBinding
        attrs = {"id": "teams_by_object_table", "class": "table squest-pagination-tables "}
        fields = ("object_name", "object_type", "role", "actions")
