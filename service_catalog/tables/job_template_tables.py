from django_tables2 import TemplateColumn, LinkColumn
from django_tables2.utils import A

from service_catalog.models import JobTemplate
from Squest.utils.squest_table import SquestTable


class JobTemplateTable(SquestTable):
    is_compliant = TemplateColumn(template_name='service_catalog/custom_columns/job_template_compliant.html',
                                  verbose_name="Squest compliant")
    actions = TemplateColumn(template_name='service_catalog/custom_columns/job_template_actions.html', orderable=False)
    name = LinkColumn("service_catalog:jobtemplate_details", args=[A("tower_server__id"), A("id")],
                      attrs={"td": {"class": "job_template_name"}})

    class Meta:
        row_attrs = {"id": lambda record: f'job_template_{record.id}'}
        model = JobTemplate
        attrs = {"id": "job_template_table", "class": "table squest-pagination-tables"}
        fields = ("name", "is_compliant", "actions")
