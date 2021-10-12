from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from service_catalog.models import Operation, OperationType
from django.utils.translation import ugettext_lazy as _


class OperationSerializer(ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'
        read_only = True

    def validate(self, attrs):
        if attrs['type'] == OperationType.CREATE:
            if attrs['service'].operations.filter(type=OperationType.CREATE).count() != 0:
                operation_id = attrs.get('id', None)
                if attrs['service'].operations.filter(type=OperationType.CREATE).first().id != operation_id:
                    raise ValidationError({'service': _("A service can have only one 'CREATE' operation")})
        return attrs


class AdminOperationSerializer(ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'
