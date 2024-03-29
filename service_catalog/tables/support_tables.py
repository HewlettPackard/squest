from django_tables2 import TemplateColumn, LinkColumn

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Support


class SupportTable(SquestTable):
    state = TemplateColumn(template_name='service_catalog/custom_columns/support_state.html')
    date_opened = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')
    title = LinkColumn()
    instance = LinkColumn()

    class Meta:
        model = Support
        attrs = {"id": "support_table", "class": "table squest-pagination-tables"}
        fields = ("title", "instance", "instance__service", "opened_by", "date_opened", "state")
