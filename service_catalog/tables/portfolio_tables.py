from django_tables2 import TemplateColumn

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Portfolio


class PortfolioTable(SquestTable):
    actions = TemplateColumn(template_name='custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = Portfolio
        attrs = {"id": "portfolio_table", "class": "table squest-pagination-tables"}
        fields = ("name", "description", "actions")
