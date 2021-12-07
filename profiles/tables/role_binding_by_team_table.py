from django_tables2 import tables, Column
from profiles.models import TeamRoleBinding


class RoleBindingByTeamTable(tables.Table):
    object_name = Column(verbose_name='Name')

    class Meta:
        model = TeamRoleBinding
        attrs = {"id": "teams_by_object_table", "class": "table squest-pagination-tables "}
        fields = ("object_name", "object_type", "role")
