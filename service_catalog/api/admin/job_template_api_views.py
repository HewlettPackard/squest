from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser

from service_catalog.models import JobTemplate, TowerServer
from service_catalog.serializers.job_template_serializer import JobTemplateSerializer


class JobTemplateDetails(RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = JobTemplateSerializer

    def get_queryset(self):
        tower_server = get_object_or_404(TowerServer, id=self.kwargs.get('tower_server_id', None))
        job_template_id = self.kwargs.get('pk', None)
        return JobTemplate.objects.filter(id=job_template_id, tower_server__id=tower_server.id)


class JobTemplateList(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = JobTemplateSerializer

    def get_queryset(self):
        tower_server = get_object_or_404(TowerServer, id=self.kwargs.get('tower_server_id', None))
        return JobTemplate.objects.filter(tower_server__id=tower_server.id)
