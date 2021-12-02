from django_tables2 import TemplateColumn, LinkColumn
from django_tables2.utils import A

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Doc


class DocTable(SquestTable):
    actions = TemplateColumn(template_name='custom_columns/doc_actions.html', orderable=False)
    services = TemplateColumn(template_name='custom_columns/doc_services.html', verbose_name="Linked services")
    title = LinkColumn("service_catalog:doc_show", args=[A("id")])

    class Meta:
        model = Doc
        attrs = {"id": "doc_table", "class": "table squest-pagination-tables"}
        fields = ("title", "services", "actions")
