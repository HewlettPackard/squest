from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Squest.utils.squest_api_views import SquestListAPIView, SquestRetrieveUpdateDestroyAPIView, SquestCreateAPIView, \
    SquestObjectPermissions
from service_catalog.api.serializers import RequestSerializer, AdminRequestSerializer, OperationRequestSerializer, \
    ServiceRequestSerializer
from service_catalog.filters.request_filter import RequestFilter
from service_catalog.models import Request, OperationType, Operation, Instance
from service_catalog.models.request_state import RequestState


class RequestList(SquestListAPIView):
    filterset_class = RequestFilter

    def get_queryset(self):
        return Request.get_queryset_for_user(self.request.user, 'service_catalog.view_request')

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return AdminRequestSerializer
        return RequestSerializer


class RequestDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = Request.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return AdminRequestSerializer
        return RequestSerializer

    def delete(self, request, *args, **kwargs):
        if self.get_object().state != RequestState.CANCELED and not request.user.is_superuser:
            return Response({"Error": "Request state must be 'CANCELED' to delete this request."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class SquestRequestOperationCreate(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.request_on_instance']
    }


class OperationRequestCreate(SquestCreateAPIView):
    serializer_class = OperationRequestSerializer
    queryset = Request.objects.all()

    def get_object(self):
        return get_object_or_404(Instance, id=self.kwargs.get('instance_id'))

    @swagger_auto_schema(responses={201: RequestSerializer()})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        operation = get_object_or_404(
            Operation,
            id=kwargs.get('operation_id'), type__in=[OperationType.UPDATE, OperationType.DELETE], enabled=True)

        if operation.is_admin_operation and not self.request.user.has_perm("service_catalog.admin_request_on_instance"):
            raise PermissionDenied
        if not operation.is_admin_operation and not self.request.user.has_perm("service_catalog.request_on_instance"):
            raise PermissionDenied

        serializer = self.get_serializer(operation=operation, instance=self.get_object(), user=request.user,
                                         data=request.data)
        serializer.is_valid(raise_exception=True)
        request_created = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(RequestSerializer(request_created).data, status=status.HTTP_201_CREATED, headers=headers)


class SquestRequestServiceCreate(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.request_on_service']
    }


class ServiceRequestCreate(SquestCreateAPIView):
    serializer_class = ServiceRequestSerializer
    queryset = Request.objects.all()
    permission_classes = [IsAuthenticated, SquestRequestServiceCreate]

    def get_object(self):
        return get_object_or_404(Operation, id=self.kwargs.get('pk'))

    @swagger_auto_schema(responses={201: RequestSerializer()})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        operation = get_object_or_404(
            Operation.get_queryset_for_user(request.user, 'service_catalog.request_on_service'),
            id=kwargs.get('pk'), type=OperationType.CREATE, enabled=True,
            service__id=kwargs.get('service_id'))
        serializer = self.get_serializer(operation=operation, user=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        request_created = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(RequestSerializer(request_created).data, status=status.HTTP_201_CREATED, headers=headers)
