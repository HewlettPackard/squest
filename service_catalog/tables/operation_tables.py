from django_tables2 import TemplateColumn, Column

from service_catalog.models import Operation
from Squest.utils.squest_table import SquestTable


class OperationTable(SquestTable):
    enabled = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    auto_accept = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    auto_process = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    survey = TemplateColumn(template_name='custom_columns/operation_survey.html', orderable=False)
    actions = TemplateColumn(template_name='custom_columns/operation_actions.html', orderable=False)
    approval_workflow__name = Column(verbose_name="Approval")

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("enabled", "name", "type", "job_template", "approval_workflow__name", "auto_accept", "auto_process",
                  "process_timeout_second", "survey", "actions")


class OperationTableFromInstanceDetails(SquestTable):
    name = TemplateColumn(template_name='custom_columns/operation_name.html')
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    request = TemplateColumn(template_name='custom_columns/operation_request.html', orderable=False)

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "type", "request")


class CreateOperationTable(SquestTable):
    name = TemplateColumn(template_name='custom_columns/operation_name.html')
    request = TemplateColumn(template_name='custom_columns/create_operation_request.html', orderable=False)

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "request")
