from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from profiles.api.serializers import OrganizationSerializer
from profiles.filters import OrganizationFilter
from profiles.models import Organization


class OrganizationDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()


class OrganizationListCreate(SquestListCreateAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    filterset_class = OrganizationFilter
