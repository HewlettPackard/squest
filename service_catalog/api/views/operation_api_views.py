from rest_framework.generics import get_object_or_404

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView, \
    SquestListAPIView
from service_catalog.api.serializers import OperationSerializer
from service_catalog.filters.operation_filter import OperationFilter
from service_catalog.models.instance import Instance
from service_catalog.models.operation_type import OperationType
from service_catalog.models.operations import Operation
from service_catalog.models.services import Service


class OperationListCreate(SquestListCreateAPIView):
    serializer_class = OperationSerializer
    filterset_class = OperationFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Operation.objects.none()
        return Service.objects.get(id=self.kwargs.get('service_id', None)).operations.all()

    def get_serializer_context(self):
        context = super(OperationListCreate, self).get_serializer_context()
        service = get_object_or_404(Service, pk=self.kwargs['service_id'])
        context["service"] = service
        return context


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

    def get_serializer_context(self):
        context = super(OperationDetails, self).get_serializer_context()
        service = get_object_or_404(Service, pk=self.kwargs['service_id'])
        context["service"] = service
        return context


class InstanceOperationList(SquestListAPIView):
    serializer_class = OperationSerializer

    def get_object(self):
        return get_object_or_404(Instance.get_queryset_for_user(self.request.user, "service_catalog.view_instance"),
                                 id=self.kwargs.get('instance_id', None))

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Operation.objects.none()
        return self.get_object().service.operations.exclude(type=OperationType.CREATE)
