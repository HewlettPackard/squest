from django_tables2 import CheckBoxColumn, TemplateColumn, Column, LinkColumn
from django_tables2.columns import BoundColumns
from django_tables2.utils import A

from Squest.utils.squest_table import SquestTable
from resource_tracker_v2.models import Resource


class ResourceTable(SquestTable):
    class Meta:
        model = Resource
        attrs = {"id": "resource_table", "class": "table squest-pagination-tables"}

    def __init__(self, *args, **kwargs):
        super(ResourceTable, self).__init__(*args, **kwargs)
        self.base_columns.clear()
        self.columns = BoundColumns(self, type(self).base_columns)
        if self.data.data.count() != 0:
            resource_group = self.data.data.first().resource_group
            attribute_names = list()
            for transformer in resource_group.transformers.all():
                attribute_names.append(transformer.attribute_definition.name)
            sequence = [*["selection", "name", "service_catalog_instance"], *attribute_names, *["actions"]]
            self.Meta.fields = tuple(sequence)
            self.sequence = sequence
            type(self).base_columns["selection"] = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
            type(self).base_columns["name"] = Column()
            type(self).base_columns["service_catalog_instance"] = LinkColumn("service_catalog:instance_details", args=[A("service_catalog_instance__id")], verbose_name="Instance")
            for attribute_name in attribute_names:
                type(self).base_columns[attribute_name] = TemplateColumn(
                    template_name='resource_tracker_v2/resource_group/custom_columns/attribute_value.html',
                    extra_context={'attribute_name': attribute_name},
                    orderable=False
                )
            type(self).base_columns["actions"] = TemplateColumn(template_name='resource_tracker_v2/resource_group/resources/custom_columns/resource_operations.html',
                                                                orderable=False)
            self.columns = BoundColumns(self, type(self).base_columns)
