from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from service_catalog.models import Instance
from service_catalog.serializers.instance_serializer import InstanceWriteSerializer, InstanceReadSerializer


class InstanceList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Instance.objects.all()
    serializer_class = InstanceReadSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = InstanceWriteSerializer
        return super(InstanceList, self).create(request, *args, **kwargs)


class InstanceDetails(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Instance.objects.all()
    serializer_class = InstanceReadSerializer

    def put(self, request, *args, **kwargs):
        self.serializer_class = InstanceWriteSerializer
        return super(InstanceDetails, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.serializer_class = InstanceWriteSerializer
        return super(InstanceDetails, self).patch(request, *args, **kwargs)
