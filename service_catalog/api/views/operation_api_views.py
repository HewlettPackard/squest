from guardian.shortcuts import get_objects_for_user
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from service_catalog.filters.operation_filter import OperationFilter
from service_catalog.models import Service, OperationType, Instance, Operation
from service_catalog.api.serializers import OperationSerializer, AdminOperationSerializer


class OperationListCreate(ListCreateAPIView):
    serializer_class = OperationSerializer
    filterset_class = OperationFilter

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['service'] = self.kwargs.get('service_id', None)
        return super(OperationListCreate, self).get_serializer(*args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Operation.objects.none()
        service_id = self.kwargs.get('service_id', None)
        queryset = Service.objects.get(id=service_id).operations.all()
        return queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]


class OperationDetails(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Operation.objects.none()
        service_id = self.kwargs.get('service_id', None)
        if service_id is None:
            return Operation.objects.none()
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


class InstanceOperationList(ListAPIView):
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Instance.objects.none()
        instance = get_object_or_404(get_objects_for_user(self.request.user, 'service_catalog.view_instance'),
                                     id=self.kwargs.get('instance_id', None))
        return instance.service.operations.exclude(type=OperationType.CREATE)

    permission_classes = [IsAuthenticated]
    serializer_class = OperationSerializer
