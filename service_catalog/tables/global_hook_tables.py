from django_tables2 import TemplateColumn

from Squest.utils.squest_table import SquestTable
from service_catalog.models import InstanceHook, RequestHook


class InstanceHookTable(SquestTable):
    state = TemplateColumn(template_name='service_catalog/custom_columns/global_hook_state.html')
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = InstanceHook
        attrs = {"id": "global_hook_table", "class": "table squest-pagination-tables"}
        fields = ("name", "services", "state", "job_template", "actions")

class RequestHookTable(SquestTable):
    state = TemplateColumn(template_name='service_catalog/custom_columns/global_hook_state.html')
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = RequestHook
        attrs = {"id": "global_hook_table", "class": "table squest-pagination-tables"}
        fields = ("name", "operations", "state", "job_template", "actions")
