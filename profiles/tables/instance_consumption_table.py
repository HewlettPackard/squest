from django_tables2 import LinkColumn, Table

from resource_tracker_v2.models import ResourceAttribute


class InstanceConsumptionTable(Table):

    resource__service_catalog_instance = LinkColumn(verbose_name="Instance")

    class Meta:
        model = ResourceAttribute
        attrs = {"id": "instance_consumption_table", "class": "table squest-pagination-tables"}
        fields = ("resource__service_catalog_instance", "value")
