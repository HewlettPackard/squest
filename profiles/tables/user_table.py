from django.contrib.auth.models import User
from django_tables2 import tables, TemplateColumn


class UserTable(tables.Table):
    billing_groups = TemplateColumn(template_name='custom_columns/user_billing_groups.html', orderable=False)

    class Meta:
        model = User
        attrs = {"id": "user_table", "class": "table squest-pagination-tables "}
        fields = ("username", "email", "billing_groups")
