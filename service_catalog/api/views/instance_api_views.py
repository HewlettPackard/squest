from guardian.shortcuts import get_objects_for_user
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from service_catalog.api.serializers import InstanceSerializer, InstanceReadSerializer, RestrictedInstanceReadSerializer
from service_catalog.models import Instance


class InstanceList(generics.ListCreateAPIView):

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


class InstanceDetails(generics.RetrieveUpdateAPIView):
    serializer_class = InstanceReadSerializer

    def get_permissions(self):
        if self.request.method in ["PATCH", "PUT"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return InstanceSerializer
        if self.request.user.is_superuser:
            return InstanceReadSerializer
        return RestrictedInstanceReadSerializer

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'service_catalog.view_instance')


class SpecDetailsAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        instance = get_object_or_404(Instance, id=pk)
        return Response(instance.spec, status=status.HTTP_200_OK)

    def post(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.spec = request.data
        target_instance.save()
        return Response(target_instance.spec, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.spec.update(request.data)
        target_instance.save()
        return Response(target_instance.spec, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.spec = {}
        target_instance.save()
        return Response(target_instance.spec, status=status.HTTP_204_NO_CONTENT)


class UserSpecDetailsAPIView(APIView):

    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request, pk):
        instance = get_object_or_404(get_objects_for_user(self.request.user, 'service_catalog.view_instance'), id=pk)
        return Response(instance.user_spec, status=status.HTTP_200_OK)

    def post(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.user_spec = request.data
        target_instance.save()
        return Response(target_instance.user_spec, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.user_spec.update(request.data)
        target_instance.save()
        return Response(target_instance.user_spec, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        target_instance = get_object_or_404(Instance, id=pk)
        target_instance.user_spec = {}
        target_instance.save()
        return Response(target_instance.user_spec, status=status.HTTP_204_NO_CONTENT)
