from django.utils.html import format_html
from django_tables2 import TemplateColumn, LinkColumn, CheckBoxColumn, Column

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Instance


class InstanceTable(SquestTable):
    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
    id = LinkColumn()
    quota_scope__name = Column(verbose_name='Quota scope')
    name = LinkColumn(verbose_name="Name")
    service__name = Column(verbose_name="Service")
    date_available = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')
    last_updated = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')

    def before_render(self, request):
        if not request.user.has_perm("service_catalog.delete_instance"):
            self.columns.hide('selection')

    class Meta:
        model = Instance
        attrs = {"id": "instance_table", "class": "table squest-pagination-tables"}
        fields = (
            "selection", "id", "name", "service__name", "quota_scope__name", "state", "requester", "date_available",
            "last_updated")

    def render_state(self, record, value):
        from service_catalog.views import map_instance_state
        return format_html(f'<strong class ="text-{map_instance_state(record.state)}" > {value} </strong>')

    def render_id(self, value, record):
        return f"#{value}"
