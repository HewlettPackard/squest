from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser

from service_catalog.models import JobTemplate, TowerServer
from service_catalog.serializers.job_template_serializer import JobTemplateSerializer


class JobTemplateList(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = JobTemplate.objects.all()
    serializer_class = JobTemplateSerializer


class JobTemplateDetails(RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = JobTemplate.objects.all()
    serializer_class = JobTemplateSerializer


class TowerServerJobTemplateList(ListAPIView):
    def get_queryset(self):
        tower_server = get_object_or_404(TowerServer, id=self.kwargs.get('tower_server_id', None))
        return JobTemplate.objects.filter(tower_server__id=tower_server.id)

    permission_classes = [IsAdminUser]
    serializer_class = JobTemplateSerializer
