from django_tables2 import tables, TemplateColumn, Column
from profiles.models import Role


class ScopeRoleTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/delete_scope_role.html', orderable=False)

    name = Column(linkify=True)

    class Meta:
        model = Role
        attrs = {"id": "role_table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")


class RoleTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)

    name = Column(linkify=True)

    class Meta:
        model = Role
        attrs = {"id": "role_table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")
