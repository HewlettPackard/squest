from django_tables2 import CheckBoxColumn, TemplateColumn, Column, LinkColumn
from django_tables2.columns import BoundColumns
from django_tables2.utils import A

from resource_tracker.models import Resource
from Squest.utils.squest_table import SquestTable


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
            text_attribute_names = list()
            for resource in resource_group.resources.all():
                for attribute in resource.attributes.all():
                    if attribute.attribute_type.name not in attribute_names:
                        attribute_names.append(attribute.attribute_type.name)
                for attribute in resource.text_attributes.all():
                    if attribute.text_attribute_type.name not in text_attribute_names:
                        text_attribute_names.append(attribute.text_attribute_type.name)
            sequence = [*["selection", "name", "service_catalog_instance"], *attribute_names, *text_attribute_names, *["operations"]]
            self.Meta.fields = tuple(sequence)
            self.sequence = sequence
            type(self).base_columns["selection"] = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
            type(self).base_columns["name"] = Column()
            type(self).base_columns["service_catalog_instance"] = LinkColumn("service_catalog:instance_details", args=[A("service_catalog_instance__id")], verbose_name="Instance")
            for attribute_name in attribute_names:
                type(self).base_columns[attribute_name] = TemplateColumn(
                    template_name='custom_columns/attribute_value.html',
                    extra_context={'attribute_name': attribute_name},
                    orderable=False
                )
            for attribute_name in text_attribute_names:
                type(self).base_columns[attribute_name] = TemplateColumn(
                    template_name='custom_columns/text_attribute_value.html',
                    extra_context={'attribute_name': attribute_name},
                    orderable=False
                )
            type(self).base_columns["operations"] = TemplateColumn(template_name='custom_columns/resource_operations.html', orderable=False)
            self.columns = BoundColumns(self, type(self).base_columns)
