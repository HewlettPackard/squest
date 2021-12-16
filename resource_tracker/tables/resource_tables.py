from django_tables2 import CheckBoxColumn, TemplateColumn
from django_tables2.columns import BoundColumns

from resource_tracker.models import Resource
from Squest.utils.squest_table import SquestTable


class ResourceTable(SquestTable):
    class Meta:
        model = Resource
        attrs = {"id": "resource_table", "class": "table squest-pagination-tables"}
        fields = ("selection", "name", "operations")
    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}})
    operations = TemplateColumn(template_name='custom_columns/resource_operations.html', orderable=False)

    def __init__(self, *args, **kwargs):
        super(ResourceTable, self).__init__(*args, **kwargs)
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
            sequence = [*["selection", "name"], *attribute_names, *text_attribute_names, *["operations"]]
            self.Meta.fields = tuple(sequence)
            self.sequence = sequence

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
            type(self).base_columns.move_to_end("operations")
            self.columns = BoundColumns(self, type(self).base_columns)
