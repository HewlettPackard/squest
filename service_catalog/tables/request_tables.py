from django.utils.html import format_html
from django_tables2 import TemplateColumn, LinkColumn, CheckBoxColumn
from django_tables2.utils import A

from service_catalog.models import Request
from Squest.utils.squest_table import SquestTable


class RequestTable(SquestTable):
    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
    id = LinkColumn("service_catalog:request_details", args=[A("id")])
    date_submitted = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')
    operation = LinkColumn()
    instance = LinkColumn()

    def before_render(self, request):
        if request.user.is_superuser:
            self.columns.show('user__username')
            self.columns.show('selection')
        else:
            self.columns.hide('user__username')
            self.columns.hide('selection')

    class Meta:
        model = Request
        attrs = {"id": "request_table", "class": "table squest-pagination-tables"}
        fields = ("selection", "id", "instance", "user__username", "date_submitted", "instance__service", "operation",
                  "state")

    def render_state(self, record, value):
        from service_catalog.views import map_request_state
        return format_html(f'<strong class="text-{ map_request_state(value) }">{ value }</strong>')
