from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A

from service_catalog.models import Support
from Squest.utils.squest_table import SquestTable


class SupportTable(SquestTable):
    state = TemplateColumn(template_name='custom_columns/support_state.html')
    date_opened = TemplateColumn(template_name='custom_columns/generic_date_format.html')
    title = LinkColumn()
    instance = LinkColumn()

    class Meta:
        model = Support
        attrs = {"id": "support_table", "class": "table squest-pagination-tables"}
        fields = ("title", "instance", "opened_by", "date_opened", "state")
