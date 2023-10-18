from django_tables2 import LinkColumn

from Squest.utils.squest_table import SquestTable
from resource_tracker_v2.models import ResourceAttribute


class InstanceConsumptionTable(SquestTable):

    resource__service_catalog_instance = LinkColumn(verbose_name="Instance")

    class Meta:
        model = ResourceAttribute
        attrs = {"id": "instance_consumption_table", "class": "table squest-pagination-tables"}
        fields = ("resource__service_catalog_instance", "resource__service_catalog_instance__requester", "value")
