from guardian.shortcuts import get_objects_for_user
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from service_catalog.models import RequestState, Service
from service_catalog.api.serializers import RequestSerializer, AdminRequestSerializer, OperationRequestSerializer, ServiceRequestSerializer


class RequestList(ListAPIView):
    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_request')

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return AdminRequestSerializer
        return RequestSerializer

    permission_classes = [IsAuthenticated]


class RequestDetails(RetrieveUpdateDestroyAPIView):
    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return AdminRequestSerializer
        return RequestSerializer

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_request')

    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def delete(self, request, *args, **kwargs):
        target_request = get_object_or_404(get_objects_for_user(request.user, 'service_catalog.view_request'),
                                           id=kwargs.get('pk'))
        if request.user.is_superuser or target_request.state == RequestState.CANCELED:
            target_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if target_request.state != RequestState.CANCELED:
            return Response({"Error": "Request state must be 'CANCELED' to delete this request."},
                            status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_403_FORBIDDEN)


class OperationRequestCreate(CreateAPIView):
    """
    Archive the request : change the state of the request to 'ARCHIVED'.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OperationRequestSerializer


class ServiceRequestCreate(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceRequestSerializer
    queryset = Service.objects.all()
