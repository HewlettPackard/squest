from rest_framework.generics import get_object_or_404

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView, \
    SquestListAPIView, SquestObjectPermissions
from service_catalog.filters.operation_filter import OperationFilter
from service_catalog.models.services import Service
from service_catalog.models.operation_type import OperationType
from service_catalog.models.operations import Operation
from service_catalog.models.instance import Instance
from service_catalog.api.serializers import OperationSerializer


class OperationListCreate(SquestListCreateAPIView):
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


class OperationDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = OperationSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Operation.objects.none()
        service_id = self.kwargs.get('service_id', None)
        if service_id is None:
            return Operation.objects.none()
        queryset = Service.objects.get(id=service_id).operations.all()
        return queryset


class InstanceOperationList(SquestListAPIView):
    serializer_class = OperationSerializer

    def get_object(self):
        return get_object_or_404(Instance.get_queryset_for_user(self.request.user,"service_catalog.view_instance"), id=self.kwargs.get('instance_id', None))

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Instance.objects.none()
        return self.get_object().service.operations.exclude(type=OperationType.CREATE)
