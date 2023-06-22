from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from profiles.api.serializers import OrganizationSerializer
from profiles.filters import OrganizationFilter
from profiles.models import Organization


class OrganizationDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminUser]
    queryset = Organization.objects.all()


class OrganizationListCreate(ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminUser]
    queryset = Organization.objects.all()
    filterset_class = OrganizationFilter
