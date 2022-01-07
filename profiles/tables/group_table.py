from django.contrib.auth.models import Group
from django_tables2 import tables, TemplateColumn


class GroupTable(tables.Table):
    actions = TemplateColumn(template_name='custom_columns/group_actions.html', orderable=False)
    users = TemplateColumn(template_name='custom_columns/group_users.html', orderable=False)

    class Meta:
        model = Group
        attrs = {"id": "group_table", "class": "table squest-pagination-tables "}
        fields = ("name", "users", "actions")
