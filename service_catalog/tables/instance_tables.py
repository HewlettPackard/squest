from django.utils.html import format_html
from django_tables2 import TemplateColumn, LinkColumn, CheckBoxColumn
from django_tables2.utils import A

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Instance


class InstanceTable(SquestTable):
    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
    service = LinkColumn()
    opened_support_count = TemplateColumn(template_name='service_catalog/custom_columns/instance_opened_support.html',
                                          verbose_name="Opened support")
    name = LinkColumn("service_catalog:instance_details", args=[A("id")], verbose_name="Name")
    quota_scope = LinkColumn()
    def before_render(self, request):
        if not request.user.has_perm("service_catalog.delete_instance"):
            self.columns.hide('selection')

    class Meta:
        model = Instance
        attrs = {"id": "instance_table", "class": "table squest-pagination-tables"}
        fields = ("selection", "name", "service", "quota_scope", "state", "opened_support_count", "requester", "date_available")

    def render_state(self, record, value):
        from service_catalog.views import map_instance_state
        return format_html(f'<strong class ="text-{ map_instance_state(value) }" > { value } </strong>')
