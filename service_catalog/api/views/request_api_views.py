from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from Squest.utils.squest_api_views import SquestListAPIView, SquestRetrieveUpdateDestroyAPIView, SquestCreateAPIView, \
    SquestObjectPermissions
from service_catalog.api.serializers import RequestSerializer, AdminRequestSerializer, OperationRequestSerializer, \
    ServiceRequestSerializer
from service_catalog.filters.request_filter import RequestFilter
from service_catalog.models import Request, OperationType, Operation, Instance


class RequestList(SquestListAPIView):
    filterset_class = RequestFilter

    def get_queryset(self):
        return Request.get_queryset_for_user(self.request.user, 'service_catalog.view_request').prefetch_related(
            "user", "operation", "instance__requester", "instance__requester__profile", "instance__resources",
            "instance__requester__groups", "instance__quota_scope", "instance__service",
            "operation__service", "approval_workflow_state", "approval_workflow_state__approval_workflow",
            "approval_workflow_state__current_step",
            "approval_workflow_state__current_step__approval_step", "approval_workflow_state__approval_step_states"
        )

    def get_serializer_class(self):
        if self.request.user.has_perm("service_catalog.view_admin_survey"):
            return AdminRequestSerializer
        else:
            return RequestSerializer


class RequestDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = Request.objects.all()

    def get_object(self):
        if getattr(self, "swagger_fake_view", False):
            return Request.objects.none()
        return super().get_object()

    def get_serializer_class(self):
        if self.request.user.has_perm("service_catalog.view_admin_survey", self.get_object()):
            return AdminRequestSerializer
        else:
            return RequestSerializer


class OperationRequestCreate(SquestCreateAPIView):
    serializer_class = OperationRequestSerializer
    queryset = Request.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Instance, id=self.kwargs.get('instance_id'))

    @swagger_auto_schema(responses={201: RequestSerializer()})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        operation = get_object_or_404(
            Operation,
            id=kwargs.get('operation_id'), type__in=[OperationType.UPDATE, OperationType.DELETE], enabled=True)

        serializer = self.get_serializer(operation=operation, instance=self.get_object(), user=request.user,
                                         data=request.data)
        serializer.is_valid(raise_exception=True)
        request_created = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(RequestSerializer(request_created).data, status=status.HTTP_201_CREATED, headers=headers)


class SquestRequestServiceCreatePermissions(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['service_catalog.request_on_service']
    }

    def has_object_permission(self, request, view, obj):
        # Override to raise 403 instead of 404
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)

        if not user.has_perms(perms, obj):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise PermissionDenied

            # Has read permissions.
            return False

        return True


class ServiceRequestCreate(SquestCreateAPIView):
    serializer_class = ServiceRequestSerializer
    queryset = Request.objects.all()
    permission_classes = [IsAuthenticated, SquestRequestServiceCreatePermissions]

    def get_object(self):
        return get_object_or_404(Operation, id=self.kwargs.get('pk'), type=OperationType.CREATE, enabled=True,
                                 service_id=self.kwargs.get('service_id'))

    @swagger_auto_schema(responses={201: RequestSerializer()})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        operation = self.get_object()
        serializer = self.get_serializer(operation=operation, user=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        request_created = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(RequestSerializer(request_created).data, status=status.HTTP_201_CREATED, headers=headers)
