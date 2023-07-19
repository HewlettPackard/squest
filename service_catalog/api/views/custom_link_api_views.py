from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from service_catalog.api.serializers.custom_link_serializer import CustomLinkSerializer
from service_catalog.filters.custom_link_filter import CustomLinkFilter
from service_catalog.models.custom_link import CustomLink


class CustomLinkDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = CustomLink.objects.all()
    serializer_class = CustomLinkSerializer


class CustomLinkListCreate(SquestListCreateAPIView):
    filterset_class = CustomLinkFilter
    serializer_class = CustomLinkSerializer
    queryset = CustomLink.objects.all()
