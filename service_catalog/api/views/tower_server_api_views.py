from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from service_catalog.filters.tower_server_filter import TowerServerFilter
from service_catalog.models import TowerServer
from service_catalog.api.serializers import TowerServerSerializer, TowerServerCreateSerializer


class TowerServerList(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = TowerServer.objects.all()
    filterset_class = TowerServerFilter

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return TowerServerCreateSerializer
        return TowerServerSerializer


class TowerServerDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = TowerServer.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return TowerServerCreateSerializer
        return TowerServerSerializer
