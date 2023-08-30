from rest_framework import serializers

from resource_tracker_v2.models import Transformer


class TransformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transformer
        fields = ["id", "resource_group", "attribute_definition", "consume_from_resource_group",
                  "consume_from_attribute_definition", "factor", "total_consumed", "total_produced",
                  "yellow_threshold_percent_consumed", "red_threshold_percent_consumed"]
        read_only_fields = ["total_consumed", "total_produced"]

    def validate(self, data):
        super(TransformerSerializer, self).validate(data)

        resource_group = self.instance.resource_group if self.instance else None
        resource_group = data.get("resource_group") if "resource_group" in data.keys() else resource_group

        attribute_definition = self.instance.attribute_definition if self.instance else None
        attribute_definition = data.get("attribute_definition") if "attribute_definition" in data.keys() else attribute_definition

        consume_from_resource_group = self.instance.consume_from_resource_group if self.instance else None
        consume_from_resource_group = data.get("consume_from_resource_group") if "consume_from_resource_group" in data.keys() else consume_from_resource_group

        consume_from_attribute = self.instance.consume_from_attribute_definition if self.instance else None
        consume_from_attribute = data.get("consume_from_attribute_definition") if "consume_from_attribute_definition" in data.keys() else consume_from_attribute

        if consume_from_resource_group is not None and consume_from_attribute is None:
            raise serializers.ValidationError(
                {"consume_from_attribute_definition": "'consume_from_attribute_definition' cannot "
                                                      "be empty if 'consume_from_resource_group' is set"})
        if consume_from_resource_group is None and consume_from_attribute is not None:
            raise serializers.ValidationError(
                {"consume_from_resource_group": "'consume_from_resource_group' cannot be empty if "
                                                "'consume_from_attribute' is set"})

        # check if the target attribute is defined as transformer
        if consume_from_resource_group is not None and consume_from_attribute is not None:
            if Transformer.objects.filter(resource_group=consume_from_resource_group,
                                          attribute_definition=consume_from_attribute).count() == 0:
                raise serializers.ValidationError(
                    {"consume_from_attribute": f"Selected attribute '{consume_from_attribute.name}' is "
                                               f"not a valid attribute of the resource group "
                                               f"'{consume_from_resource_group.name}'"})

            if Transformer.is_loop_consumption_detected(source_resource_group=resource_group,
                                                        source_attribute=attribute_definition,
                                                        target_resource_group=consume_from_resource_group,
                                                        target_attribute=consume_from_attribute):
                raise serializers.ValidationError(
                    {"consume_from_attribute_definition": f"Circular loop detected on resource "
                                                          f"group '{resource_group.name}'"})
        return data
