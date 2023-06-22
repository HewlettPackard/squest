from django_tables2 import tables, TemplateColumn

from profiles.models import RBAC


class RBACTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/group_actions.html', orderable=False)
    users = TemplateColumn(template_name='custom_columns/group_users.html', orderable=False)

    class Meta:
        model = RBAC
        attrs = {"id": "group_table", "class": "table squest-pagination-tables "}
        fields = ("name", "users", "actions")
