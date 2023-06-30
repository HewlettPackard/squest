from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.generics import get_object_or_404, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from service_catalog.api.serializers import InstanceSerializer, InstanceReadSerializer, \
    RestrictedInstanceReadSerializer, InstanceSerializerUserSpec, InstanceSerializerSpec
from service_catalog.filters.instance_filter import InstanceFilter
from service_catalog.models import Instance


class InstanceList(ListCreateAPIView):
    filterset_class = InstanceFilter
    permission_classes = (IsAuthenticated, )
    def get_queryset(self):
        return Instance.get_queryset_for_user(self.request.user, 'service_catalog.view_instance')

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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT", "DELETE"]:
            return InstanceSerializer
        if self.request.user.is_superuser:
            return InstanceReadSerializer
        return RestrictedInstanceReadSerializer


class SpecDetailsAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = InstanceSerializerSpec
    queryset = Instance.objects.all()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.spec, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        target_instance = self.get_object()
        target_instance.spec = request.data
        target_instance.save()
        return Response(target_instance.spec, status=HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        target_instance = self.get_object()
        target_instance.spec.update(request.data)
        target_instance.save()
        return Response(target_instance.spec, status=HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        target_instance = self.get_object()
        target_instance.spec = {}
        target_instance.save()
        return Response(target_instance.spec, status=HTTP_204_NO_CONTENT)


class UserSpecDetailsAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
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
