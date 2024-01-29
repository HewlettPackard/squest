from django.utils.html import format_html
from django_tables2 import LinkColumn, TemplateColumn

from Squest.utils.squest_table import SquestTable
from profiles.models import Scope


class ApprovalWorkflowPreviewTable(SquestTable):

    name = LinkColumn()
    preview = TemplateColumn(template_name='profiles/custom_columns/preview_workflow.html', orderable=False)

    class Meta:
        model = Scope
        attrs = {"id": "role_table", "class": "table squest-pagination-tables"}
        fields = ("name", "preview")

    def render_name(self, value, record):
        return format_html(f'<a title={record} href="{record.get_absolute_url()}">{record}</a>')
