from django_tables2 import TemplateColumn, LinkColumn
from django_tables2.utils import A

from Squest.utils.squest_table import SquestTable
from service_catalog.models import TowerServer


class TowerServerTable(SquestTable):
    name = LinkColumn()
    host = TemplateColumn(template_name='service_catalog/custom_columns/tower_server_host.html')
    jobtemplate = TemplateColumn(template_name='service_catalog/custom_columns/tower_server_job_templates.html',
                                 verbose_name="Job templates")
    actions = TemplateColumn(template_name='service_catalog/custom_columns/tower_server_actions.html', orderable=False)

    class Meta:
        model = TowerServer
        attrs = {"id": "tower_server_table", "class": "table squest-pagination-tables"}
        fields = ("name", "host", "jobtemplate", "actions")
