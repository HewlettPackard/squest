from django_tables2 import TemplateColumn, LinkColumn

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Operation


class OperationTable(SquestTable):
    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("enabled", "name", "type", "job_template", "auto_accept", "auto_process",
                  "permission", "actions")

    name = LinkColumn()
    enabled = TemplateColumn(template_name='generics/custom_columns/generic_boolean.html')
    type = TemplateColumn(template_name='service_catalog/custom_columns/operation_type.html')
    auto_accept = TemplateColumn(template_name='generics/custom_columns/generic_boolean.html')
    auto_process = TemplateColumn(template_name='generics/custom_columns/generic_boolean.html')
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)


class OperationTableFromInstanceDetails(SquestTable):
    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "type", "auto_accept", "auto_process", "actions")

    type = TemplateColumn(template_name='service_catalog/custom_columns/operation_type.html')
    auto_accept = TemplateColumn(template_name='generics/custom_columns/generic_boolean.html')
    auto_process = TemplateColumn(template_name='generics/custom_columns/generic_boolean.html')
    actions = TemplateColumn(template_name='service_catalog/custom_columns/operation_request.html', orderable=False,
                             verbose_name="")


class CreateOperationTable(SquestTable):
    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "auto_accept", "auto_process", "actions")

    auto_accept = TemplateColumn(template_name='generics/custom_columns/generic_boolean.html')
    auto_process = TemplateColumn(template_name='generics/custom_columns/generic_boolean.html')
    actions = TemplateColumn(template_name='service_catalog/custom_columns/create_operation_request.html',
                            orderable=False)
