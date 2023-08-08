from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import TemplateColumn, LinkColumn, Column
from django_tables2.utils import A

from Squest.utils.squest_table import SquestTable


class UserTable(SquestTable):
    username = LinkColumn("profiles:user_details", args=[A("id")])

    class Meta:
        model = User
        attrs = {"id": "user_table", "class": "table squest-pagination-tables "}
        fields = ("username", "email",)


class UserRoleTable(SquestTable):
    username = Column()
    roles = TemplateColumn(template_name='profiles/custom_columns/user_roles.html', orderable=False)
    actions = TemplateColumn(template_name='profiles/custom_columns/delete_all_user_roles.html', orderable=False)

    class Meta:
        model = User
        attrs = {"id": "organization_table", "class": "table squest-pagination-tables"}
        fields = ("username", "roles")

    def render_username(self, record):
        url = reverse('service_catalog:instance_list')
        return format_html(f"<a href='{url}?requester={record.id}'>{record}</a>")
