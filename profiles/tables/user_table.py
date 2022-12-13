from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import tables, TemplateColumn, A, LinkColumn


class UserTable(tables.Table):
    username = LinkColumn("service_catalog:instance_list")
    billing_groups = TemplateColumn(template_name='custom_columns/user_billing_groups.html', orderable=False)

    def render_username(self, record):
        url = reverse('service_catalog:instance_list')
        return format_html(f"<a href='{url}?spoc={record.id}'>{record}</a>")

    class Meta:
        model = User
        attrs = {"id": "user_table", "class": "table squest-pagination-tables "}
        fields = ("username", "email", "billing_groups")
