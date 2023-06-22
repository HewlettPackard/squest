from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import LinkColumn, Column

from Squest.utils.squest_table import SquestTable
from profiles.models import Team


class TeamTable(SquestTable):
    name = Column(linkify=True)
    org = Column(linkify=True)
    users = Column(orderable=False)

    class Meta:
        model = Team
        attrs = {"id": "team_table", "class": "table squest-pagination-tables"}
        fields = ("name", "org", "users")

    def render_users(self, value, record):
        link = reverse("profiles:team_details", kwargs={'pk': record.id})
        return format_html(f'<a href="{link}#users" class="btn btn-default bg-sm">{record.users.count()}</a>')


class TeamUserTable(SquestTable):
    username = Column()

    class Meta:
        model = User
        attrs = {"id": "team_table", "class": "table squest-pagination-tables"}
        fields = ("username",)

    def render_username(self, record):
        url = reverse('service_catalog:instance_list')
        return format_html(f"<a href='{url}?requester={record.id}'>{record}</a>")
