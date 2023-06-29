from guardian.shortcuts import get_objects_for_user
from rest_framework import status
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.generics import get_object_or_404, ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Squest.utils.squest_rbac import SquestObjectPermissions
from service_catalog.api.serializers import InstanceSerializer, InstanceReadSerializer, \
    RestrictedInstanceReadSerializer, InstanceSerializerUserSpec, InstanceSerializerSpec
from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.models import Instance


class InstanceList(ListCreateAPIView):
    filterset_class = InstanceFilter

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_instance')

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return InstanceSerializer
        else:
            if self.request.user.is_superuser:
                return InstanceReadSerializer
        return RestrictedInstanceReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance_created = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(InstanceReadSerializer(instance_created).data, status=status.HTTP_201_CREATED, headers=headers)


class InstanceDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = InstanceReadSerializer
    queryset = Instance.objects.all()
    permission_classes = [SquestObjectPermissions, IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT", "DELETE"]:
            return InstanceSerializer
        if self.request.user.is_superuser:
            return InstanceReadSerializer
        return RestrictedInstanceReadSerializer


class SpecDetailsAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [SquestObjectPermissions, IsAdminUser, IsAuthenticated]
    serializer_class = InstanceSerializerSpec

    def get(self, request, pk):
        instance = get_object_or_404(Instance, id=pk)
        return Response(instance.spec, status=HTTP_200_OK)

    def post(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.spec = request.data
        target_instance.save()
        return Response(target_instance.spec, status=HTTP_201_CREATED)

    def patch(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.spec.update(request.data)
        target_instance.save()
        return Response(target_instance.spec, status=HTTP_200_OK)

    def delete(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.spec = {}
        target_instance.save()
        return Response(target_instance.spec, status=HTTP_204_NO_CONTENT)


class UserSpecDetailsAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [SquestObjectPermissions, IsAuthenticated]
    serializer_class = InstanceSerializerUserSpec
    def get(self, request, pk):
        instance = get_object_or_404(Instance, id=pk)
        return Response(instance.user_spec, status=HTTP_200_OK)

    def post(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.user_spec = request.data
        target_instance.save()
        return Response(target_instance.user_spec, status=HTTP_201_CREATED)

    def patch(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.user_spec.update(request.data)
        target_instance.save()
        return Response(target_instance.user_spec, status=HTTP_200_OK)

    def delete(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.user_spec = {}
        target_instance.save()
        return Response(target_instance.user_spec, status=HTTP_204_NO_CONTENT)
