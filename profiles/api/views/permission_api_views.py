from django.contrib.auth.models import Permission
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers import PermissionSerializer
from profiles.filters import PermissionFilter


class PermissionDetails(RetrieveAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]
    queryset = Permission.objects.all()


class PermissionList(ListAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]
    queryset = Permission.objects.all()
    filterset_class = PermissionFilter
