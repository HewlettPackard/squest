from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A

from service_catalog.models.approval_workflow import ApprovalWorkflow


class ApprovalWorkflowTable(tables.Table):
    name = LinkColumn("service_catalog:approval_step_graph", args=[A("id")])

    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = ApprovalWorkflow
        attrs = {"id": "approval_workflow_table", "class": "table squest-pagination-tables "}
        fields = ("name", "actions")
