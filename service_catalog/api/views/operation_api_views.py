from guardian.shortcuts import get_objects_for_user
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from service_catalog.models import Service, OperationType
from service_catalog.api.serializers import OperationSerializer, AdminOperationSerializer


class OperationListCreate(ListCreateAPIView):
    serializer_class = OperationSerializer

    def get_queryset(self):
        service_id = self.kwargs.get('service_id', None)
        queryset = Service.objects.get(id=service_id).operations.all()
        return queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        request.data['service'] = self.kwargs.get('service_id', None)
        return super(OperationListCreate, self).create(request, *args, **kwargs)


class OperationDetails(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        service_id = self.kwargs.get('service_id', None)
        if service_id is None:
            return Service.objects.none()
        queryset = Service.objects.get(id=service_id).operations.all()
        return queryset

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return AdminOperationSerializer
        return OperationSerializer

    def get_permissions(self):
        if self.request.method in ["DELETE", "PATCH", "PUT"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def delete(self, request, *args, **kwargs):
        operation = Service.objects.get(id=self.kwargs['service_id']).operations.all().get(id=self.kwargs['pk'])
        if operation.type == OperationType.CREATE:
            return Response({"Error": "You cannot delete a create operation of a service."},
                            status=status.HTTP_403_FORBIDDEN)
        return super(OperationDetails, self).delete(request, *args, **kwargs)


class InstanceOperationList(ListAPIView):
    def get_queryset(self):
        instance = get_object_or_404(get_objects_for_user(self.request.user, 'service_catalog.view_instance'), id=self.kwargs.get('instance_id', None))
        return instance.service.operations.exclude(type=OperationType.CREATE)

    permission_classes = [IsAuthenticated]
    serializer_class = OperationSerializer
