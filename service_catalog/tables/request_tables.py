from django_tables2 import TemplateColumn, LinkColumn, CheckBoxColumn
from django_tables2.utils import A

from service_catalog.models import Request
from Squest.utils.squest_table import SquestTable


class RequestTable(SquestTable):
    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
    id = LinkColumn("service_catalog:request_details", args=[A("id")])
    actions = TemplateColumn(template_name='custom_columns/request_actions.html', orderable=False)
    state = TemplateColumn(template_name='custom_columns/request_state.html')
    operation__type = TemplateColumn(verbose_name="Type", template_name='custom_columns/request_operation_type.html')
    instance__name = LinkColumn("service_catalog:instance_details", args=[A("instance__id")],
                                verbose_name="Instance")

    def before_render(self, request):
        if request.user.is_superuser:
            self.columns.show('user')
            self.columns.show('selection')
        else:
            self.columns.hide('user')
            self.columns.hide('selection')

    class Meta:
        model = Request
        attrs = {"id": "request_table", "class": "table squest-pagination-tables"}
        fields = ("selection", "id", "instance__name", "user", "date_submitted", "instance__service__name", "operation__name",
                  "operation__type", "state", "actions")
