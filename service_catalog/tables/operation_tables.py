from django_tables2 import TemplateColumn, LinkColumn

from service_catalog.models import Operation
from Squest.utils.squest_table import SquestTable


class OperationTable(SquestTable):
    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("enabled", "name", "type", "job_template", "auto_accept", "auto_process",
                  "is_admin_operation", "actions")

    enabled = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    auto_accept = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    auto_process = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    is_admin_operation = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    actions = TemplateColumn(template_name='custom_columns/operation_actions.html', orderable=False)


class OperationTableFromInstanceDetails(SquestTable):
    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "type", "is_admin_operation", "request")

    name = LinkColumn()
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    request = TemplateColumn(template_name='custom_columns/operation_request.html', orderable=False)
    is_admin_operation = TemplateColumn(template_name='custom_columns/generic_boolean.html')


class CreateOperationTable(SquestTable):
    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "is_admin_operation", "request")

    name = LinkColumn()
    request = TemplateColumn(template_name='custom_columns/create_operation_request.html', orderable=False)
    is_admin_operation = TemplateColumn(template_name='custom_columns/generic_boolean.html')
