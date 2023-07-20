from django.utils.html import format_html
from django_tables2 import TemplateColumn, Column

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Announcement


class AnnouncementTable(SquestTable):
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)
    created_by__username = Column(verbose_name='Owner')

    class Meta:
        model = Announcement
        attrs = {"id": "announcement_table", "class": "table squest-pagination-tables"}
        fields = ("title", "date_start", "date_stop", "created_by__username", "type", "actions")

    def render_type(self, value, record):
        return format_html(f'<strong class="text-{ value.lower() }">{ value }</strong>')
