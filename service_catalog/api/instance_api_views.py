from guardian.shortcuts import get_objects_for_user
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from service_catalog.serializers.instance_serializer import InstanceWriteSerializer, InstanceReadSerializer


class InstanceList(generics.ListCreateAPIView):
    serializer_class = InstanceReadSerializer

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_instance')

    def create(self, request, *args, **kwargs):
        self.serializer_class = InstanceWriteSerializer
        return super(InstanceList, self).create(request, *args, **kwargs)


class InstanceDetails(generics.RetrieveUpdateAPIView):
    serializer_class = InstanceReadSerializer

    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return InstanceWriteSerializer
        return InstanceReadSerializer

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_instance')

    def put(self, request, *args, **kwargs):
        self.serializer_class = InstanceWriteSerializer
        return super(InstanceDetails, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.serializer_class = InstanceWriteSerializer
        return super(InstanceDetails, self).patch(request, *args, **kwargs)
