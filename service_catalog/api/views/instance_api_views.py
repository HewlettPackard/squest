from guardian.shortcuts import get_objects_for_user
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from service_catalog.api.serializers import InstanceSerializer, InstanceReadSerializer


class InstanceList(generics.ListCreateAPIView):

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_instance')

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return InstanceSerializer
        return InstanceReadSerializer


class InstanceDetails(generics.RetrieveUpdateAPIView):
    serializer_class = InstanceReadSerializer

    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return InstanceSerializer
        return InstanceReadSerializer

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_instance')
