from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser
from service_catalog.models import TowerServer
from service_catalog.serializers.tower_server_serializer import TowerServerSerializer, TowerServerCreateSerializer


class TowerServerList(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = TowerServer.objects.all()
    serializer_class = TowerServerSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = TowerServerCreateSerializer
        return super(TowerServerList, self).create(request, *args, **kwargs)


class TowerServerDetails(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = TowerServer.objects.all()
    serializer_class = TowerServerSerializer

    def put(self, request, *args, **kwargs):
        self.serializer_class = TowerServerCreateSerializer
        return super(TowerServerDetails, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.serializer_class = TowerServerCreateSerializer
        return super(TowerServerDetails, self).patch(request, *args, **kwargs)
