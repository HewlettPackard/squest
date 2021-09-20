from django_tables2 import TemplateColumn

from service_catalog.models import Operation
from utils.squest_table import SquestTable


class OperationTable(SquestTable):
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    auto_accept = TemplateColumn(template_name='custom_columns/operation_boolean.html')
    auto_process = TemplateColumn(template_name='custom_columns/operation_boolean.html')
    survey = TemplateColumn(template_name='custom_columns/operation_survey.html', orderable=False)
    actions = TemplateColumn(template_name='custom_columns/operation_actions.html', orderable=False)

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "type", "job_template", "auto_accept", "auto_process", "process_timeout_second", "survey",
                  "actions")


class OperationTableFromInstanceDetails(SquestTable):
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    request = TemplateColumn(template_name='custom_columns/operation_request.html', orderable=False)

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "type", "request")
