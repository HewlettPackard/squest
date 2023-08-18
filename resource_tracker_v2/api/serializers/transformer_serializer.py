from rest_framework import serializers

from resource_tracker_v2.models import Transformer


class TransformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transformer
        fields = ["id", "resource_group", "attribute_definition", "consume_from_resource_group",
                  "consume_from_attribute_definition", "factor", "total_consumed", "total_produced",
                  "yellow_threshold_percent_consumed", "red_threshold_percent_consumed"]
        read_only_fields = ["resource_group", "total_consumed", "total_produced"]

    def __init__(self, *args, **kwargs):
        self.resource_group = kwargs['context'].get('resource_group')
        super(TransformerSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        super(TransformerSerializer, self).validate(data)
        current_id = None if self.instance is None else self.instance.id
        attribute_definition = data.get("attribute_definition")
        consume_from_resource_group = data.get("consume_from_resource_group")
        consume_from_attribute = data.get("consume_from_attribute_definition")
        if self.instance is not None:
            if 'attribute_definition' not in data.keys():
                attribute_definition = self.instance.attribute_definition
            if 'consume_from_resource_group' not in data.keys():
                consume_from_resource_group = self.instance.consume_from_resource_group
            if 'consume_from_attribute_definition' not in data.keys():
                consume_from_attribute = self.instance.consume_from_attribute_definition
        if Transformer.objects.exclude(pk=current_id).filter(resource_group=self.resource_group, attribute_definition=attribute_definition).exists():
            raise serializers.ValidationError(
                {"attribute_definition": f"A Transformer already exist for {attribute_definition} in {self.resource_group}"})

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

            if Transformer.is_loop_consumption_detected(source_resource_group=self.resource_group,
                                                        source_attribute=attribute_definition,
                                                        target_resource_group=consume_from_resource_group,
                                                        target_attribute=consume_from_attribute):
                raise serializers.ValidationError(
                    {"consume_from_attribute_definition": f"Circular loop detected on resource "
                                                          f"group '{self.resource_group.name}'"})
        return data

    def create(self, validated_data):
        validated_data['resource_group'] = self.resource_group
        return super().create(validated_data)
