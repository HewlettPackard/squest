from django.utils.html import format_html
from django_tables2 import TemplateColumn, Column

from Squest.utils.squest_table import SquestTable
from profiles.models import Role


class ScopeRoleTable(SquestTable):
    name = Column(linkify=True)

    class Meta:
        model = Role
        attrs = {"id": "role_table", "class": "table squest-pagination-tables"}
        fields = ("name",)


class RoleTable(SquestTable):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)
    name = Column(linkify=True)

    class Meta:
        model = Role
        attrs = {"id": "role_table", "class": "table squest-pagination-tables"}
        fields = ("name",)


class RoleAssignementUserTable(SquestTable):
    scope = Column(orderable=False)
    username = Column(orderable=False)

    def render_scope(self, value, record):
        return format_html(
            f'<a title={record["scope"]["name"]} href="{record["scope"]["url"]}">{record["scope"]["name"]}</a>')


class RoleAssignementScopeTable(SquestTable):
    scope = Column(orderable=False)

    def render_scope(self, value, record):
        return format_html(
            f'<a title={record["scope"]["name"]} href="{record["scope"]["url"]}">{record["scope"]["name"]}</a>')
