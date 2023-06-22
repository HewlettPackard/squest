from django.contrib.auth.models import Permission
from django_tables2 import tables


class PermissionTable(tables.Table):

    class Meta:
        model = Permission
        attrs = {"id": "permission_table", "class": "table squest-pagination-tables "}
        fields = ("name", "codename", "content_type")
