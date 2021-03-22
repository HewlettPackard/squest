from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from service_catalog.models import Instance
from service_catalog.serializers.instance_serializer import InstanceSerializer


class InstanceList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer


class InstanceDetails(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer

