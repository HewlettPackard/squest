from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from service_catalog.api.serializers.custom_link_serializer import CustomLinkSerializer
from service_catalog.filters.custom_link_filter import CustomLinkFilter
from service_catalog.models.custom_link import CustomLink


class CustomLinkDetails(RetrieveUpdateDestroyAPIView):
    queryset = CustomLink.objects.all()
    serializer_class = CustomLinkSerializer

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsAdminUser()]
        return [IsAuthenticated()]


class CustomLinkListCreate(ListCreateAPIView):
    filterset_class = CustomLinkFilter
    serializer_class = CustomLinkSerializer
    queryset = CustomLink.objects.all()

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsAdminUser()]
        return [IsAuthenticated()]
