from django_tables2 import tables, TemplateColumn

from profiles.models.squest_permission import Permission


class PermissionTable(tables.Table):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = Permission
        attrs = {"id": "permission_table", "class": "table squest-pagination-tables"}
        fields = ("name", "codename", "content_type__model")
