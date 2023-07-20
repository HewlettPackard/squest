from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import tables

from resource_tracker_v2.models import ResourceAttribute


class InstanceConsumptionTable(tables.Table):

    class Meta:
        model = ResourceAttribute
        attrs = {"id": "instance_consumption_table", "class": "table squest-pagination-tables"}
        fields = ("resource", "value")

    def render_resource(self, record, value):
        link = reverse("service_catalog:instance_details", kwargs={'pk': record.resource.service_catalog_instance.id})
        return format_html(f'<a href="{link}">{record.resource.service_catalog_instance.name}</a>')
