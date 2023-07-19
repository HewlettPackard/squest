from django_tables2 import TemplateColumn

from service_catalog.models import Service
from Squest.utils.squest_table import SquestTable


class ServiceTable(SquestTable):
    actions = TemplateColumn(template_name='custom_columns/service_actions.html', orderable=False)
    enabled = TemplateColumn(template_name='custom_columns/generic_boolean_check.html')
    operations = TemplateColumn(template_name='custom_columns/service_operations.html',
                                verbose_name="Operations", orderable=False)

    class Meta:
        model = Service
        attrs = {"id": "service_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "enabled", "operations", "actions")
