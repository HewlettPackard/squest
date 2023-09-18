
from django.utils.html import format_html
from django_tables2 import TemplateColumn, LinkColumn, CheckBoxColumn, Column
from django_tables2.utils import A

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Instance


class InstanceTable(SquestTable):
    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
    quota_scope__name = Column(verbose_name='Quota scope')
    name = LinkColumn()
    date_available = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')
    last_updated = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')

    def before_render(self, request):
        if not request.user.has_perm("service_catalog.delete_instance"):
            self.columns.hide('selection')

    class Meta:
        model = Instance
        attrs = {"id": "instance_table", "class": "table squest-pagination-tables"}
        fields = ("selection", "name", "service__name", "quota_scope__name", "state", "requester", "date_available", "last_updated")

    def render_state(self, record, value):
        from service_catalog.views import map_instance_state
        return format_html(f'<strong class ="text-{ map_instance_state(record.state) }" > { value } </strong>')
