from django_tables2 import TemplateColumn, Column

from service_catalog.models import JobTemplate
from utils.squest_table import SquestTable


class JobTemplateTable(SquestTable):
    compliant = TemplateColumn(template_name='custom_columns/job_template_compliant.html',
                               verbose_name="Squest compliant")
    actions = TemplateColumn(template_name='custom_columns/job_template_actions.html', orderable=False)
    name = Column(attrs={"td": {"class": "job_template_name"}})

    class Meta:
        row_attrs = {"id": lambda record: f'job_template_{record.id}'}
        model = JobTemplate
        attrs = {"id": "job_template_table", "class": "table squest-pagination-tables"}
        fields = ("name", "compliant", "actions")
