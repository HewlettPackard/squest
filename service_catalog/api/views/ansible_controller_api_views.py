from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from service_catalog.api.serializers import AnsibleControllerSerializer, AnsibleControllerCreateSerializer
from service_catalog.filters.ansible_controller_filter import AnsibleControllerFilter
from service_catalog.models import AnsibleController


class AnsibleControllerList(SquestListCreateAPIView):
    queryset = AnsibleController.objects.all()
    filterset_class = AnsibleControllerFilter

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return AnsibleControllerCreateSerializer
        return AnsibleControllerSerializer


class AnsibleControllerDetails(SquestRetrieveUpdateDestroyAPIView):
    queryset = AnsibleController.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return AnsibleControllerCreateSerializer
        return AnsibleControllerSerializer
