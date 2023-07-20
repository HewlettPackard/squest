from django_tables2 import tables, TemplateColumn, Column
from profiles.models import Role


class ScopeRoleTable(tables.Table):
    name = Column(linkify=True)

    class Meta:
        model = Role
        attrs = {"id": "role_table", "class": "table squest-pagination-tables"}
        fields = ("name",)


class RoleTable(tables.Table):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)
    name = Column(linkify=True)

    class Meta:
        model = Role
        attrs = {"id": "role_table", "class": "table squest-pagination-tables"}
        fields = ("name",)
