from django_tables2 import TemplateColumn, Column

from service_catalog.models import Announcement
from Squest.utils.squest_table import SquestTable


class AnnouncementTable(SquestTable):
    actions = TemplateColumn(template_name='custom_columns/announcement_actions.html', orderable=False)
    type = TemplateColumn(template_name='custom_columns/announcement_type.html')
    created_by__username = Column(verbose_name='Owner')

    class Meta:
        model = Announcement
        attrs = {"id": "announcement_table", "class": "table squest-pagination-tables"}
        fields = ("title", "date_start", "date_stop", "created_by__username", "type", "actions")
