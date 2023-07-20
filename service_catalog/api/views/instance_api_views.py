from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView, \
    SquestRetrieveUpdateAPIView, SquestObjectPermissions
from service_catalog.api.serializers import InstanceSerializer, InstanceReadSerializer, \
    RestrictedInstanceReadSerializer, InstanceSerializerUserSpec, InstanceSerializerSpec
from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.models import Instance


class InstanceList(SquestListCreateAPIView):
    filterset_class = InstanceFilter

    def get_queryset(self):
        return Instance.get_queryset_for_user(self.request.user, 'service_catalog.view_instance')

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return InstanceSerializer
        elif self.request.user.has_perm('service_catalog.view_admin_spec_instance'):
            return InstanceReadSerializer
        return RestrictedInstanceReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance_created = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(InstanceReadSerializer(instance_created).data, status=status.HTTP_201_CREATED, headers=headers)


class InstanceDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = InstanceReadSerializer
    queryset = Instance.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT", "DELETE"]:
            return InstanceSerializer
        elif self.request.user.has_perm('service_catalog.view_admin_spec_instance'):
            return InstanceReadSerializer
        return RestrictedInstanceReadSerializer


class SquestAdminSpecPermissionsDetails(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_admin_spec_instance'],
        'OPTIONS': [],
        'HEAD': [],
        'PUT': ['%(app_label)s.change_admin_spec_instance'],
        'PATCH': ['%(app_label)s.change_admin_spec_instance'],
    }


class SpecDetailsAPIView(SquestRetrieveUpdateAPIView):
    serializer_class = InstanceSerializerSpec
    queryset = Instance.objects.all()
    permission_classes = [IsAuthenticated, SquestAdminSpecPermissionsDetails]

    def get(self, request, *args, **kwargs):
        return Response(self.get_object().spec, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.spec = request.data
        instance.save()
        return Response(instance.spec, status=HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.spec.update(request.data)
        instance.save()
        return Response(instance.spec, status=HTTP_200_OK)


class UserSpecDetailsAPIView(SquestRetrieveUpdateAPIView):
    serializer_class = InstanceSerializerUserSpec
    queryset = Instance.objects.all()

    def get(self, request, *args, **kwargs):
        return Response(self.get_object().user_spec, status=HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        target_instance = self.get_object()
        target_instance.user_spec = request.data
        target_instance.save()
        return Response(target_instance.user_spec, status=HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        target_instance = self.get_object()
        target_instance.user_spec.update(request.data)
        target_instance.save()
        return Response(target_instance.user_spec, status=HTTP_200_OK)
