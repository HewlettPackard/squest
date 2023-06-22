from django_tables2 import TemplateColumn, Column

from service_catalog.models import Operation
from Squest.utils.squest_table import SquestTable


class OperationTable(SquestTable):
    enabled = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    auto_accept = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    auto_process = TemplateColumn(template_name='custom_columns/generic_boolean.html')
    is_admin_operation = TemplateColumn(template_name='custom_columns/generic_boolean.html', verbose_name="Admin only")
    actions = TemplateColumn(template_name='custom_columns/operation_actions.html', orderable=False)

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("enabled", "name", "type", "job_template", "auto_accept", "auto_process",
                  "is_admin_operation", "actions")


class OperationTableFromInstanceDetails(SquestTable):
    name = TemplateColumn(template_name='custom_columns/operation_name.html')
    type = TemplateColumn(template_name='custom_columns/operation_type.html')
    is_admin_operation = TemplateColumn(template_name='custom_columns/generic_boolean.html', verbose_name="Admin only")
    request = TemplateColumn(template_name='custom_columns/operation_request.html', orderable=False)

    def before_render(self, request):
        if not request.user.is_superuser:
            self.columns.hide('is_admin_operation')

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "type", "is_admin_operation", "request")


class CreateOperationTable(SquestTable):
    name = TemplateColumn(template_name='custom_columns/operation_name.html')
    is_admin_operation = TemplateColumn(template_name='custom_columns/generic_boolean.html', verbose_name="Admin only")
    request = TemplateColumn(template_name='custom_columns/create_operation_request.html', orderable=False)

    def before_render(self, request):
        if not request.user.is_superuser:
            self.columns.hide('is_admin_operation')

    class Meta:
        model = Operation
        attrs = {"id": "operation_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "is_admin_operation", "request")
