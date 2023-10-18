from django_tables2 import TemplateColumn, Column

from Squest.utils.squest_table import SquestTable
from profiles.models.squest_permission import Permission


class PermissionTable(SquestTable):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)
    content_type__model = Column(verbose_name="Model")

    class Meta:
        model = Permission
        attrs = {"id": "permission_table", "class": "table squest-pagination-tables"}
        fields = ("name", "codename", "content_type__model")
