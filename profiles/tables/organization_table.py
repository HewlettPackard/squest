from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import Column

from Squest.utils.squest_table import SquestTable
from profiles.models import Organization


class OrganizationTable(SquestTable):
    name = Column(linkify=True)
    users = Column(orderable=False)
    teams = Column(orderable=False)

    class Meta:
        model = Organization
        attrs = {"id": "organization_table", "class": "table squest-pagination-tables"}
        fields = ("name", "users", "teams")

    def render_users(self, value, record):
        link = reverse("profiles:organization_details", kwargs={'pk': record.id})
        return format_html(f'<a href="{link}#users" class="btn btn-default bg-sm">{record.users.count()}</a>')

    def render_teams(self, value, record):
        link = reverse("profiles:organization_details", kwargs={'pk': record.id})
        return format_html(f'<a href="{link}#teams" class="btn btn-default bg-sm">{record.teams.count()}</a>')

