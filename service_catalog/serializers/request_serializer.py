from rest_framework import serializers

from service_catalog.models import Request
from service_catalog.serializers.instance_serializer import InstanceSerializer


class RequestSerializer(serializers.ModelSerializer):

    instance = InstanceSerializer()

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request", None)
        if request and request.user and request.user.is_superuser is False:
            for field in fields.values():
                field.read_only = True
        return fields

    class Meta:
        model = Request
        exclude = ['periodic_task', 'periodic_task_date_expire', 'failure_message']
