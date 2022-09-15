from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from service_catalog.filters.service_filter import ServiceFilter
from service_catalog.models import Service
from service_catalog.api.serializers import ServiceSerializer, AdminServiceSerializer


class ServiceListCreate(ListCreateAPIView):
    filterset_class = ServiceFilter

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return AdminServiceSerializer
        return ServiceSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Service.objects.none()
        if self.request.user.is_superuser:
            return Service.objects.all()
        return Service.objects.filter(enabled=True)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED, headers=headers)


class ServiceDetails(RetrieveUpdateDestroyAPIView):
    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return AdminServiceSerializer
        return ServiceSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Service.objects.none()
        if self.request.user.is_superuser:
            return Service.objects.all()
        return Service.objects.filter(enabled=True)

    def get_permissions(self):
        if self.request.method in ["DELETE", "PATCH", "PUT"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]
