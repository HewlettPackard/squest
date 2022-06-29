from django_tables2 import TemplateColumn

from service_catalog.models import Service
from Squest.utils.squest_table import SquestTable


class ServiceTable(SquestTable):
    actions = TemplateColumn(template_name='custom_columns/service_actions.html', orderable=False)
    enabled = TemplateColumn(template_name='custom_columns/boolean_check.html')
    operations = TemplateColumn(template_name='custom_columns/service_operations.html',
                                verbose_name="Operations", orderable=False)

    def before_render(self, request):
        if request.user.is_superuser:
            self.columns.show('enabled')
            self.columns.show('operations')
        else:
            self.columns.hide('enabled')
            self.columns.hide('operations')

    class Meta:
        model = Service
        attrs = {"id": "service_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "enabled", "operations", "actions")
