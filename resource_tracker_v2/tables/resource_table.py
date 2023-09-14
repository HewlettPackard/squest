from django_tables2 import CheckBoxColumn, TemplateColumn, Column, LinkColumn
from django_tables2.columns import BoundColumns
from django_tables2.utils import A

from Squest.utils.squest_table import SquestTable
from resource_tracker_v2.models import Resource


class ResourceTable(SquestTable):
    class Meta:
        model = Resource
        attrs = {"id": "resource_table", "class": "table squest-pagination-tables"}
        fields = ("selection", "name", "service_catalog_instance")

    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
    service_catalog_instance = LinkColumn(verbose_name="Instance")

    def __init__(self, *args, **kwargs):
        kwargs["extra_columns"] = list()
        if "data" in kwargs.keys():
            if kwargs["data"].count() != 0:
                resource_group = kwargs["data"].first().resource_group
                for attribute_name in resource_group.transformers.values_list('attribute_definition__name', flat=True):
                    kwargs["extra_columns"].append((attribute_name, TemplateColumn(
                        template_name='resource_tracker_v2/resource_group/custom_columns/attribute_value.html',
                        extra_context={'attribute_name': attribute_name},
                        orderable=False
                    )))
        kwargs["extra_columns"].append(("Actions", TemplateColumn(
            template_name='resource_tracker_v2/resource_group/resources/custom_columns/resource_operations.html',
            orderable=False
        )))
        super(ResourceTable, self).__init__(*args, **kwargs)
