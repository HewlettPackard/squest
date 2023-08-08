from django_tables2 import TemplateColumn, LinkColumn
from django_tables2.utils import A

from Squest.utils.squest_table import SquestTable
from service_catalog.models import AnsibleController


class AnsibleControllerTable(SquestTable):
    name = LinkColumn()
    host = TemplateColumn(template_name='service_catalog/custom_columns/ansible_controller_host.html')
    jobtemplate = TemplateColumn(template_name='service_catalog/custom_columns/ansible_controller_job_templates.html',
                                 verbose_name="Job templates")
    actions = TemplateColumn(template_name='service_catalog/custom_columns/ansible_controller_actions.html', orderable=False)

    class Meta:
        model = AnsibleController
        attrs = {"id": "ansible_controller_table", "class": "table squest-pagination-tables"}
        fields = ("name", "host", "jobtemplate", "actions")
