from django.utils.html import format_html
from django_tables2 import TemplateColumn, LinkColumn, A

from Squest.utils.squest_table import SquestTable
from service_catalog.models import ApprovalWorkflow


class ApprovalWorkflowTable(SquestTable):
    name = LinkColumn("service_catalog:approvalworkflow_details", args=[A("id")])
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = ApprovalWorkflow
        attrs = {"id": "approval_workflow_table", "class": "table squest-pagination-tables "}
        fields = ("name", "operation", "scopes", "enabled", "actions")

    def render_scopes(self, value, record):
        scopes = record.scopes.all().distinct()
        html = ""
        for scope in scopes:
            html += f"<span class=\"badge bg-primary\">{scope}</span>  "
        return format_html(html)
